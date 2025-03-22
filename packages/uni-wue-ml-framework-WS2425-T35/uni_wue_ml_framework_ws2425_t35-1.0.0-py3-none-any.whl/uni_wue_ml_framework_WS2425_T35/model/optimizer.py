class __Optimizer:
    """
    Abstract base class for all optimzers.
    """
    def __init__(self, layers, learning_rate, repr):
        self.layers = layers
        self.learning_rate = learning_rate
        self.repr = repr
    
    def __repr__(self):
        """
        Returns a string respresentation of the optimzers object. 
        """
        return self.repr

class GradientDescent(__Optimizer):
    """
    A usual gradient descent optimzer.
    """
    def __init__(self, layers, learning_rate):
        super().__init__(layers=layers, learning_rate=learning_rate, repr='GradientDescent')

    def update(self):
        for layer in self.layers:
            layer.weights -= self.learning_rate * layer.grad_weights
            layer.biases -= self.learning_rate * layer.grad_biases
