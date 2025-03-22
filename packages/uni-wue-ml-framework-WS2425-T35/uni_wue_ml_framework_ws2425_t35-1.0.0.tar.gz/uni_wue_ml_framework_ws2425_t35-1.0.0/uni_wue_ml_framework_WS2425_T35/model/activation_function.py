import numpy as np

from .derivable_function import _DerivableFunction

##################################################
# Activation function helpers
# Do not use this directly.
##################################################

# Sigmoid
def __sigmoid(z): return 1 / (1 + np.exp(-z)) #def __sigmoid(z): return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))
def __sigmoid_deriv(z): return z * (1 - z)
# tanh
def __tangh(z): return (np.exp(z) - np.exp(-z)) / (np.exp(z) + np.exp(-z))
def __tangh_deriv(z): return 1 - __tangh(z)
# ReLu
def __relu(z): return np.where(z > 0, z, 0)
def __relu_deriv(z): return (z > 0).astype(float)


##################################################
# Activation functions
##################################################
sigmoid = _DerivableFunction(__sigmoid, __sigmoid_deriv, 'sigmoid')
sigmoid.__doc__ += "\nSigmoid activation function."
tanh = _DerivableFunction(__tangh, __tangh_deriv, 'tanh')
tanh.__doc__ += "\nTangens hyperbolicus activation function."
relu = _DerivableFunction(__relu, __relu_deriv, 'relu')
tanh.__doc__ += "\nReLu activation function."