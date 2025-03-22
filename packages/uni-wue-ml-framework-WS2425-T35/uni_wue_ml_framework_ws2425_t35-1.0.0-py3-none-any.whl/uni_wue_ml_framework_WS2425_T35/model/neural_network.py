import numpy as np
import matplotlib.pyplot as plt
#from pickle import load, dump

from uni_wue_ml_framework_WS2425_T35.utils import Storable
from uni_wue_ml_framework_WS2425_T35.evaluation import root_mean_squared_error, r2_score, accuracy, recall_macro_avg, precision_macro_avg, f1_macro_avg
from uni_wue_ml_framework_WS2425_T35.model.layer import Layer
from uni_wue_ml_framework_WS2425_T35.model.optimizer import GradientDescent
from uni_wue_ml_framework_WS2425_T35.model.cost_function import softmax

##################################################
# Model
##################################################
class NeuralNetwork(Storable):    
    def __init__(self, hidden_layer_sizes, activation, loss_func, task='regression',
                 epochs=100, learning_rate=0.001, batch_size=None, early_stopping=12,
                 optimizer=GradientDescent,  train_statistic_metrics=None,
                 random_state=None, verbose=0):
        """
        hidden_layer_sizes:
            An iterable of the sizes of hidden layers.
        activation:Func
            The activation function.
        loss_func:Func
            The loss function.
        task='regression':
            Regression if task='regression' else classifiction.
        epochs=100:
            The amount of training cycles using the whole train set.
        learning_rate=0.001:
            The learning rate to adjust parameters.
        batch_size=None:
            If None the whole training data is used in one batch.
            If an integer batch_size > 0, batch_size randomly selected samples are used.
        early_stopping=8:
            If early_stopping and validation set is passed in fit, it will stop after 
            early_stopping epoch iterations without an improvement of the validation loss.
            If not early_stopping or no validation set is passed, it will iter all epochs. 
        optimizer:
            The optimizer to update layer weights and biases.
            A class of type optimizer.__Optimizer, that can be instanziated as 
            optimizer(self.layers, self.learning_rate). 
        random_state=None:
            If None batch and weight initialisations are random, otherwise a seed is used. 
        verbose=0:
            The amount of information that is printed during training process.
        """
        self.task = task
        self.rng = np.random.RandomState(random_state)
        self.layers = None # Initialised in fit
        self.optimizer = optimizer # Initialised in fit
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.loss_func = loss_func
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.early_stopping = early_stopping
        self.verbose = verbose
        self.statistics = False
        if train_statistic_metrics is None:
            self.train_statistic_metrics = {
                'RMSE':root_mean_squared_error,
                'R2':r2_score
            } if self.task == 'regression' else {
                'accuracy':accuracy,
                'recall_macro_avg':recall_macro_avg,
                'precision_macro_avg':precision_macro_avg,
                'f1_macro_avg':f1_macro_avg
            }

    def predict_raw(self, X:np.ndarray):
        """
        Forwards input through the network and returns the raw result.
        In case of classification returns the values before using softmax.
        Params:
            X:np.ndarray
                Numpy array of shape (n_samples, n_features)
        Returns: 
            Predictions as a Numpy array of shape (n_samples, 1) in case of regression.
            Predictions as a Numpy array of shape (n_samples, n_classes) in case of classification.
        """
        for layer in self.layers[:-1]:
            X = self.activation(layer.forward(X))
        return self.layers[-1].forward(X)

    def predict_proba(self, X:np.ndarray):
        """
        Predicts values.
        Returns values after softmax in case of classification.
        Params:
            X:np.ndarray
                Numpy array of shape (n_samples, n_features).
        Returns: 
            Predictions as a Numpy array of shape (n_samples, 1) in case of regression.
            Predictions as a Numpy array of shape (n_samples, n_classes) in case of classification.
        """
        out = self.predict_raw(X)
        return out if self.task == 'regression' else softmax(out)
    
    def predict(self, X:np.ndarray):
        """
        Predict values. 
        Params:
            X:np.ndarray
                Numpy array of shape (n_samples, n_features).
        Returns: Predictions as a Numpy array of shape  (n_samples, ).
        """
        out = self.predict_proba(X)
        return out[:,0] if self.task == 'regression' else self.classes[out.argmax(axis=1)]
        

    def fit(self, X:np.ndarray, y:np.ndarray, X_val:np.ndarray=None, y_val:np.ndarray=None):
        """
        Fit the model.
        Params:
            X:np.ndarray
                Numpy array of shape (n_samples, n_features).
            y:np.ndarray
                Numpy array of shape (n_samples, ).
            X_val/y_val:np.ndarray=None
                If not None: Used to create validation test statistics.
                Shapes according to X/y (while n_samples can differ).
        """
        assert X.shape[0] == y.shape[0]
        assert X_val is None or X.shape[1] == X_val.shape[1]
        assert X_val is None or X_val.shape[0] == y_val.shape[0]
        if X_val is not None:
            assert y_val is not None
            def init():
                s = {m:[] for m in self.train_statistic_metrics}
                s['loss'] = []
                return s
            #self.statistics = {t:{'loss':[], 'metric':[]} for t in ['train', 'val']}
            self.statistics = {t:init() for t in ['train', 'val']}
            self.statistics['epoch'] = []
        
        # Adjust input shapes
        #if y.ndim == 1:
        if self.task == 'regression':
            y_internal = y.reshape(-1,1)
            if y_val is not None: y_val_internal = y_val.reshape(-1,1)
        else:
            self.classes = np.unique(y)
            def expand(y): return (np.repeat(y, self.classes.shape[0]).reshape(y.shape[0], -1) == self.classes).astype('float64')
            y_internal = expand(y)
            if y_val is not None: y_val_internal = expand(y_val)
        
        # Init layers
        layer_sizes = [X.shape[1], *self.hidden_layer_sizes, y_internal.shape[1]]
        self.layers = [Layer(layer_sizes[i], layer_sizes[i + 1], self.rng) for i in range(len(layer_sizes) - 1)]
        best_layers = self.layers # in case of early stopping, the layers with the best validation set performance will be used
        
        # Init optimzer
        self.optimizer = self.optimizer(self.layers, self.learning_rate)

        # Train: no pain no gain
        n_samples = X.shape[0]
        batch_size = n_samples if self.batch_size is None else self.batch_size
        best_loss = np.inf
        n_epochs_no_improvement = 0
        for epoch in range(self.epochs):
            total_loss = 0
            # Shuffle data for random sampled batches
            indices = np.arange(n_samples)
            self.rng.shuffle(indices)
            X = X[indices]
            y = y[indices]
            y_internal = y_internal[indices]

            for start_idx in range(0, n_samples, batch_size):
                end_idx = min(start_idx + batch_size, n_samples)
                batch_X = X[start_idx:end_idx]
                batch_y = y_internal[start_idx:end_idx]

                # Forward pass
                activations = []
                x = batch_X
                for layer in self.layers[:-1]:
                    x = self.activation(layer.forward(x))
                    activations.append(x)
                output = self.layers[-1].forward(x)
                if self.task != 'regression':
                    output = softmax(output)

                # Compute loss
                loss = self.loss_func(batch_y, output) #+ sum((l.weights**2).sum() for l in self.layers)/batch_size
                total_loss += loss * (end_idx - start_idx) / n_samples

                # Backward pass
                grad = self.loss_func.derivative(batch_y, output)
                grad = self.layers[-1].backward(grad)

                for j in range(len(self.layers) - 2, -1, -1):
                    grad = grad * self.activation.derivative(activations[j])
                    grad = self.layers[j].backward(grad)

                # Update weights and biases
                self.optimizer.update()

            # Evaluation statistics
            if self.verbose and (epoch + 1) % (self.epochs / 10) == 0:
                print(f'Epoch {epoch + 1}/{self.epochs}, Loss: {total_loss}')
            if X_val is not None and (epoch + 1) % (self.epochs / min(100, self.epochs)) == 0:
                self.statistics['epoch'].append(epoch)
                self.statistics['train']['loss'].append(total_loss)
                self.statistics['val']['loss'].append(self.loss_func(y_val_internal, self.predict_proba(X_val)))
                #f = root_mean_squared_error if self.task == 'regression' else accuracy
                #def stats(X, y, t): self.statistics[t]['metric'].append(f(y, self.predict(X)))
                def stats(X, y, t): 
                    y_pred = self.predict(X)
                    for metric in self.train_statistic_metrics:
                        self.statistics[t][metric].append(self.train_statistic_metrics[metric](y, y_pred))
                stats(X, y, 'train')
                stats(X_val, y_val, 'val')

            # Early stopping
            if self.early_stopping and X_val is not None:
                if best_loss > total_loss:
                    best_loss = total_loss
                    n_epochs_no_improvement = 0
                    best_layers = [l.copy() for l in self.layers]
                else:
                    n_epochs_no_improvement += 1
                if n_epochs_no_improvement >= self.early_stopping:
                    if self.verbose: print(f'Early stopping at epoch {epoch}')
                    self.layers = best_layers
                    return self
        return self

    def plot_statistics(self, ax=None):
        """
        Plots training statistics.
        Params: 
            ax: the matplotlib axis used to plot. If None a new axis is created.
        """
        assert self.statistics
        if ax is None: _, ax = plt.subplots()
        for i, metric in enumerate(self.statistics['train']):
            ax.plot(self.statistics['epoch'], self.statistics['train'][metric], label=f'Train {metric}', c=f'C{i}', ls=':')
            ax.plot(self.statistics['epoch'], self.statistics['val'][metric], label=f'Val {metric}', c=f'C{i}')
        ax.legend()

    def __repr__(self):
        tsm = self.train_statistic_metrics.keys()
        o = repr(self.optimizer)
        return f"""NeuralNetwork(
    {self.hidden_layer_sizes=}, 
    {self.activation=},
    {self.loss_func=},
    {self.task=},
    {self.epochs=}, 
    {self.learning_rate=},
    {self.batch_size=},
    {self.early_stopping=},
    self.optimizer={o},
    self.train_statistic_metrics={tsm},
    {self.verbose=}
)"""


