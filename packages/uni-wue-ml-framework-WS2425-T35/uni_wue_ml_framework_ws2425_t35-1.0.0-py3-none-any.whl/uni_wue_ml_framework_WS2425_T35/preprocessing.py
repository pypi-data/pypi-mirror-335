import numpy as np

from uni_wue_ml_framework_WS2425_T35.utils import Storable

#############################################
# Pipeline 
#############################################
class Pipeline(Storable):
    """
    Wrapper class to perform a sequence of preprocessing steps,
    before passing data fit or predict of a model.
    """
    def __init__(self, steps, model, **kwargs):
        """
        Params: 
        steps:  A list of preprocessor objects.
                Each of it has to implement a fit_transform and transform method.
        model:  A model class, that will be instantiated using **kwargs.
        kwargs: All the arguments that should be passed for model instantiation.
        """
        self.steps = steps
        self.model = model(**kwargs)

    def fit(self, X, y, *args, X_val=None, y_val=None, **kwargs):
        """
        Performs the preprocessing steps on X and 
        fits the model on the transformed data against y.
        """
        for step in self.steps:
            X = step.fit_transform(X, *args, **kwargs)
            if X_val is not None: X_val = step.transform(X_val)
        self.model.fit(X, y, *args, X_val=X_val, y_val=y_val, **kwargs)
        #if X_val is not None: self.statistics = self.model.statistics
        return self

    def predict(self, X, *args, **kwargs):
        """
        Performs the preprocessing steps on X and returns
        the results of the models predict method.
        """
        #for step in self.steps:
        #    X = step.transform(X, *args, **kwargs)
        X = self.transform(X, *args, **kwargs)
        return self.model.predict(X, *args, **kwargs)

    def predict_proba(self, X, *args, **kwargs):
        """
        Performs the preprocessing steps on X and returns
        the results of the models predict_proba method.
        """
        X = self.transform(X, *args, **kwargs)
        return self.model.predict_proba(X, *args, **kwargs)

    def transform(self, X, *args, **kwargs):
        """
        Performs the preprocessing steps on X and returns
        the transformed data. Pipeline need to be fitted.
        """
        for step in self.steps:
            X = step.transform(X, *args, **kwargs)
        return X

    def __repr__(self):
        if len(self.steps) > 1:
            steps = '\n\t\t' + ',\n\t\t'.join(map(repr, self.steps)) + '],\n         '
        else:
            steps = self.steps[0] if len(self.steps) else ''
            steps = f"[{steps}],"
        model = repr(self.model)
        return f"Pipeline(steps=[{steps}model={model})"

#############################################
# Transformer 
#############################################
class FeatureSelection:
    """Transformer for selecting features (columns) using a mask."""
    def __init__(self, mask):
        self.mask = mask
    def transform(self, X, *args, **kwargs):
        """Returns the columns in X selected by mask"""
        return X[:,self.mask]
    def fit_transform(self, X, *args, **kwargs):
        """Returns the columns in X selected by mask"""
        return self.transform(X, *args, **kwargs)
    def __repr__(self):
        return self.__class__.__name__

class PCA:
    """
    Principal components analysis.
    """
    def __init__(self, n_components):
        """
        Params:
        n_components: the number of components that should be computed.
        """
        self.n_components = n_components
        self.components = None
        self.mean = None

    def fit(self, X, *args, **kwargs):
        """
        Fits the data X by computing the components. 
        """
        self.mean = np.mean(X, axis=0)
        cov = np.cov((X - self.mean).T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        eigenvectors = eigenvectors[:, np.argsort(eigenvalues)[::-1]]
        self.components = eigenvectors[:, :self.n_components]
        return self

    def transform(self, X, *args, **kwargs):
        """
        Transforms the data X and returns n_compnents.
        """
        return np.dot(X - self.mean, self.components)
    
    def fit_transform(self, X, *args, **kwargs):
        """
        Performs fit and transform on X in one step.
        """
        self.fit(X, *args, **kwargs)
        return self.transform(X, *args, **kwargs)

    def __repr__(self):
        return f'PCA(n_components={self.n_components})'