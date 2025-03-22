import numpy as np

#from uni_wue_ml_framework_WS2425_T35.model.derivable_function import _DerivableFunction
from .derivable_function import _DerivableFunction

##################################################
# Loss functions helpers
# Do not use this directly.
##################################################
def __cross_entropy_loss(y_true, y_pred):
    epsilon = 1e-12
    y_pred = np.clip(y_pred, epsilon, 1. - epsilon) # Ensure numerical stability
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
def __cross_entropy_loss_deriv(y_true, y_pred): return y_pred - y_true

# MSE
def __mse(y_true, y_pred): return np.mean((y_true - y_pred) ** 2)
def __mse_deriv(y_true, y_pred): return -2 * (y_true - y_pred) / y_true.shape[0]


##################################################
# Loss functions
##################################################
cross_entropy = _DerivableFunction(__cross_entropy_loss, __cross_entropy_loss_deriv, 'cross_entropy')
cross_entropy.__doc__ += "\nCross entropy loss function."
mse = _DerivableFunction(__mse, __mse_deriv, 'MSE')
cross_entropy.__doc__ += "\nMean squared error loss function."

##################################################
# Utility functions and classes
##################################################
def softmax(x):
    e = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)