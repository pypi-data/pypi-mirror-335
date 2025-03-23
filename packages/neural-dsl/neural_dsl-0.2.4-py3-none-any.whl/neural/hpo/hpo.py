import optuna
import torch
import torch.nn as nn
import torch.optim as optim
import tensorflow as tf
from torchvision.datasets import MNIST, CIFAR10
from torchvision.transforms import ToTensor
from neural.parser.parser import ModelTransformer
import keras
from neural.shape_propagation.shape_propagator import ShapePropagator
from neural.execution_optimization.execution import get_device

# Data Loader
def get_data(dataset_name, input_shape, batch_size, train=True, backend='pytorch'):
    datasets = {'MNIST': MNIST, 'CIFAR10': CIFAR10}
    dataset = datasets.get(dataset_name, MNIST)(root='./data', train=train, transform=ToTensor(), download=True)
    if backend == 'pytorch':
        return torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=train)
    elif backend == 'tensorflow':
        data = dataset.data.numpy() / 255.0  # Normalize
        targets = dataset.targets.numpy()
        if len(data.shape) == 3:  # Add channel dimension
            data = data[..., None]  # [N, H, W] → [N, H, W, 1]
        return tf.data.Dataset.from_tensor_slices((data, targets)).batch(batch_size)

def prod(iterable):
    result = 1
    for x in iterable:
        result *= x
    return result

# Factory Function
def create_dynamic_model(model_dict, trial, hpo_params, backend='pytorch'):
    if backend == 'pytorch':
        return DynamicPTModel(model_dict, trial, hpo_params)
    elif backend == 'tensorflow':
        return DynamicTFModel(model_dict, trial, hpo_params)
    raise ValueError(f"Unsupported backend: {backend}")

# Dynamic Models
class DynamicPTModel(nn.Module):
    def __init__(self, model_dict, trial, hpo_params):
        super().__init__()
        self.layers = nn.ModuleList()
        self.shape_propagator = ShapePropagator(debug=True)
        input_shape_raw = model_dict['input']['shape']
        input_shape = (None, input_shape_raw[-1], *input_shape_raw[:-1])
        current_shape = input_shape
        in_channels = input_shape[1]
        in_features = None

        # Process layers to replace HPO configurations with trial-suggested values
        for layer in model_dict['layers']:
            params = layer.get('params', {})
            if layer['type'] == 'Dense':
                units_param = params.get('units', {})
                if isinstance(units_param, dict) and 'hpo' in units_param:
                    hpo = units_param['hpo']
                    if hpo['type'] == 'categorical':
                        units = trial.suggest_categorical('dense_units', hpo['values'])
                    elif hpo['type'] == 'int_range':
                        units = trial.suggest_int('dense_units', hpo['low'], hpo['high'])
                    layer['params']['units'] = units  # Update model_dict with suggested value

        print(f"Initial shape: {current_shape}")
        for layer in model_dict['layers']:
            params = layer['params'] if layer['params'] is not None else {}
            params = params.copy()
            print(f"Before propagate: {layer['type']}, current_shape={current_shape}")
            
            if layer['type'] in ['Dense', 'Output'] and in_features is None:
                in_features = prod(current_shape[1:])
                self.layers.append(nn.Flatten())
                print(f"{layer['type']} (implicit Flatten): in_features={in_features}")
            
            current_shape = self.shape_propagator.propagate(current_shape, layer, framework='pytorch')
            print(f"After propagate: {layer['type']}, current_shape={current_shape}")
            
            if layer['type'] == 'Conv2D':
                filters = params.get('filters')
                if isinstance(filters, dict) and 'hpo' in filters:
                    hpo = filters['hpo']
                    filters = trial.suggest_int('conv_filters', hpo['low'], hpo['high'])
                else:
                    filters = filters or trial.suggest_int('conv_filters', 16, 64)
                kernel_size = params.get('kernel_size', 3)
                self.layers.append(nn.Conv2d(in_channels, filters, kernel_size))
                in_channels = filters
            elif layer['type'] == 'Flatten':
                self.layers.append(nn.Flatten())
                in_features = prod(current_shape[1:])
                print(f"Flatten: in_features={in_features}")
            elif layer['type'] == 'Dense':
                units_param = params.get('units')
                if isinstance(units_param, dict) and 'hpo' in units_param:
                    hpo = units_param['hpo']
                    if hpo['type'] == 'categorical':
                        units = trial.suggest_categorical('dense_units', hpo['values'])
                    elif hpo['type'] == 'int_range':
                        units = trial.suggest_int('dense_units', hpo['low'], hpo['high'])
                    else:
                        raise ValueError(f"Unsupported HPO type for Dense units: {hpo['type']}")
                else:
                    units = units_param if units_param is not None else trial.suggest_int('dense_units', 64, 256)
                if in_features <= 0:
                    raise ValueError(f"Invalid in_features for Dense: {in_features}")
                print(f"Dense: in_features={in_features}, units={units}")
                self.layers.append(nn.Linear(in_features, units))
                in_features = units
            elif layer['type'] == 'Output':
                units_param = params.get('units', 10)
                if isinstance(units_param, dict) and 'hpo' in units_param:
                    hpo = units_param['hpo']
                    if hpo['type'] == 'categorical':
                        units = trial.suggest_categorical('output_units', hpo['values'])
                    else:
                        raise ValueError(f"Unsupported HPO type for Output units: {hpo['type']}")
                else:
                    units = units_param
                if in_features <= 0:
                    raise ValueError(f"Invalid in_features for Output: {in_features}")
                print(f"Output: in_features={in_features}, units={units}")
                self.layers.append(nn.Linear(in_features, units))
                in_features = units
            else:
                raise ValueError(f"Unsupported layer type: {layer['type']}")
        print("Final layers:", self.layers)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
    
class DynamicTFModel(tf.keras.Model):
    def __init__(self, model_dict, trial, hpo_params):
        super().__init__()
        self.layers_list = []
        input_shape = model_dict['input']['shape']
        in_features = prod(input_shape)
        for layer in model_dict['layers']:
            params = layer['params'].copy()
            if layer['type'] == 'Dense':
                if 'hpo' in params['units']:
                    hpo = next(h for h in hpo_params if h['layer_type'] == 'Dense' and h['param_name'] == 'units')
                    units = trial.suggest_categorical('dense_units', hpo['hpo']['values'])
                    params['units'] = units
                self.layers_list.append(tf.keras.layers.Dense(params['units'], activation='relu' if params.get('activation') == 'relu' else None))
                in_features = params['units']
            elif layer['type'] == 'Dropout':
                if 'hpo' in params['rate']:
                    hpo = next(h for h in hpo_params if h['layer_type'] == 'Dropout' and h['param_name'] == 'rate')
                    rate = trial.suggest_float('dropout_rate', hpo['hpo']['start'], hpo['hpo']['end'], step=hpo['hpo']['step'])
                    params['rate'] = rate
                self.layers_list.append(tf.keras.layers.Dropout(params['rate']))
            elif layer['type'] == 'Output':
                if isinstance(params.get('units'), dict) and 'hpo' in params['units']:
                    hpo = next(h for h in hpo_params if h['layer_type'] == 'Output' and h['param_name'] == 'units')
                    units = trial.suggest_categorical('output_units', hpo['hpo']['values'])
                    params['units'] = units
                self.layers_list.append(tf.keras.layers.Dense(params['units'], activation='softmax' if params.get('activation') == 'softmax' else None))

    def call(self, inputs):
        x = tf.reshape(inputs, [inputs.shape[0], -1])  # Flatten input
        for layer in self.layers_list:
            x = layer(x)
        return x

# Training Method
def train_model(model, optimizer, train_loader, val_loader, backend='pytorch', epochs=1, execution_config=None):
    if backend == 'pytorch':
        device = get_device(execution_config.get("device", "auto") if execution_config else "auto")
        model.to(device)
        criterion = nn.CrossEntropyLoss()
        for _ in range(epochs):
            model.train()
            for data, target in train_loader:
                data, target = data.to(device), target.to(device)
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        preds, targets = [], []
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
                preds.extend(pred.cpu().numpy())
                targets.extend(target.cpu().numpy())
        from sklearn.metrics import precision_score, recall_score
        precision = precision_score(targets, preds, average='macro')
        recall = recall_score(targets, preds, average='macro')
        return val_loss / len(val_loader), correct / total, precision, recall

# HPO Objective
def objective(trial, config, dataset_name='MNIST', backend='pytorch'):
    model_dict, hpo_params = ModelTransformer().parse_network_with_hpo(config)
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])
    train_loader = get_data(dataset_name, model_dict['input']['shape'], batch_size, True)
    val_loader = get_data(dataset_name, model_dict['input']['shape'], batch_size, False)
    optimizer_config = model_dict['optimizer'] or {'type': 'Adam', 'params': {}}  # Fallback
    learning_rate_param = optimizer_config['params'].get('learning_rate', 0.001)
    if isinstance(learning_rate_param, dict) and 'hpo' in learning_rate_param:
        hpo = learning_rate_param['hpo']
        if hpo['type'] == 'log_range':
            lr = trial.suggest_float("learning_rate", hpo['low'], hpo['high'], log=True)
        elif hpo['type'] == 'range':
            lr = trial.suggest_float("learning_rate", hpo['start'], hpo['end'], step=hpo.get('step', 1))
        elif hpo['type'] == 'categorical':
            lr = trial.suggest_categorical("learning_rate", hpo['values'])
    else:
        lr = float(learning_rate_param)

    model = create_dynamic_model(model_dict, trial, hpo_params, backend)
    if backend == 'pytorch':
        optimizer = getattr(optim, optimizer_config['type'])(model.parameters(), lr=lr)
    elif backend == 'tensorflow':
        optimizer = tf.keras.optimizers.get({'class_name': optimizer_config['type'], 'config': {'learning_rate': lr}})

    val_loss, val_acc, precision, recall = train_model(model, optimizer, train_loader, val_loader, backend)
    return val_loss, -val_acc, precision, recall  # Negative accuracy for minimization

# Optimize and Return
def optimize_and_return(config, n_trials=10, dataset_name='MNIST', backend='pytorch'):
    study = optuna.create_study(directions=["minimize", "minimize", "maximize", "maximize"])
    study.optimize(lambda trial: objective(trial, config, dataset_name, backend), n_trials=n_trials)
    return study.best_trials[0].params