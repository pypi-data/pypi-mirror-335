
##################################################
# Base class for activations and loss functions.
##################################################
class _DerivableFunction:
    """
    Base class for activations and loss functions.
    """
    def __init__(self, f, df, repr):
        """
        f: activation/loss function itself
        df: derivative of the activation/loss function 
        repr: a small string that could be used to represent the object.
        """
        self.f = f
        self.df = df
        self.repr = repr

    def __call__(self, *args):
        """
        Returns the the result of the function. 
        """
        return self.f(*args)

    def derivative(self, *args):
        """
        Returns the result of the derivative. 
        """
        return self.df(*args)

    def __repr__(self):
        """
        Returns a string respresentation of the function object. 
        """
        return self.repr