import numpy as np

class Layer:
    """
    Internal class used to represent a layer.
    """
    def __init__(self, input_size, output_size, rng, weights=None, biases=None):
        if weights is None:
            self.weights = rng.randn(input_size, output_size) * np.sqrt(2 / input_size)
            self.biases = np.zeros((1, output_size))
        else:
            self.weights = weights
            self.biases = biases
    
    def forward(self, x):
        self.input = x
        return np.dot(x, self.weights) + self.biases
    
    def backward(self, grad_output):
        # Gradient w.r.t. weights / biases
        self.grad_weights = np.dot(self.input.T, grad_output)
        self.grad_biases = np.sum(grad_output, axis=0, keepdims=True)
        # Gradient w.r.t. respect to input
        return np.dot(grad_output, self.weights.T)

    def copy(self):
        return self.__class__(None, None, None, self.weights.copy(), self.biases.copy())
