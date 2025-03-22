import numpy as np
import pandas as pd
from pprint import pprint, pformat
from itertools import product
from pickle import dump, load

from .utils import Storable
from .preprocessing import Pipeline

def train_test_split(*args, test_size, random_state=None):
    """
    Performs a train test split similar to the sklearn implementation.
    I.e. X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    """
    if isinstance(test_size, float):
        test_size = int(len(args[0])*test_size)
    indicies = np.arange(len(args[0]))
    rng = np.random.RandomState(random_state)
    rng.shuffle(indicies)
    for x in args:
        if isinstance(x, pd.DataFrame):
            x = x.iloc
        yield x[indicies[test_size:]]
        yield x[indicies[:test_size]]

class GridSearch(Storable):
    def __init__(self, model, grid, k_folds, scoring, refit=False, random_state=None, verbose=1):
        """
        Performs a k-fold hyperparamter grid search.
        Params:
            model:       The class of a model
            grid:        A dictonary with parameter names as keys and a list of parameters as values.
            k_folds:     The number of folds on which to evaluate the each parameter combination.
            scoring:     A dictionary with metric names as keys and a function 
                         f(y_true, y_pred) that returns a metric score.
            refit=False: If False no final model is created. Else it has to be the name of ones of the metrics
                         specified in the scoring dictionary. This metric will be used to choose the best 
                         hyperparameter combination to retrain a model on the whole dataset.
            random_state=None: A random state used to split the folds. 
            verbose=1:   Controls the amount of information that is printed during training process.
        """
        self.model = model
        self.grid = grid
        self.k_folds = k_folds
        self.scoring = scoring
        self.refit = refit
        self.random_state = random_state
        self.verbose = verbose

    def fit(self, X, y, *, X_val=None, y_val=None):
        """
        Performs the hyperparamter grid search.
        Params:
            X: Train feature set
            y: Train target
            X_val=None: Validation feature set
            y_val=None: Validation target
        """
        n_samples = len(X)
        n_per_fold = n_samples // self.k_folds
        indices = np.arange(n_samples)
        np.random.RandomState(self.random_state).shuffle(indices)
        
        self.results = {}
        grid = tuple(product(*self.grid.values()))

        # Iter hyperparameter grid
        for i, kwargs in enumerate([dict(zip(self.grid.keys(), args)) for args in grid]):
            runs = []
            if self.verbose: 
                print('-----------------------------------------------------------')
                print(f'Params {i+1}/{len(grid)}')
                print('-----------------------------------------------------------')
                pprint(kwargs)

            # Cross validation
            for j in range(self.k_folds):
                if self.verbose > 1: print(f'Run {j+1}/{self.k_folds}')

                # Test fold indices  
                from_, to_ = (n_per_fold*j, n_per_fold*(j+1)) if j + 1 < self.k_folds else (n_per_fold*j, n_samples)

                # Train test split
                test_indices = indices[from_:to_]
                train_indices = np.append(indices[:from_], indices[to_:])
                X_train, y_train = X[train_indices], y[train_indices]
                X_test, y_test = X[test_indices], y[test_indices]

                # Instantiate model and train
                model = self.model(**kwargs).fit(X_train, y_train, X_val=X_val, y_val=y_val)

                # Evaluate results
                y_pred = model.predict(X_test)
                run = {metric:self.scoring[metric](y_test, y_pred) for metric in self.scoring}
                if X_val is not None: run['train_statistics'] = (model.model if isinstance(model, Pipeline) else model).statistics 
                runs.append(run)

            # Save results
            self.results[tuple([tuple(a) if isinstance(a, list) else a for a in kwargs.values()])] = runs
            #self.results[tuple(kwargs.values())] = runs

        # Refit model with best parameters on the whole train set 
        if self.refit:
            res_by = self.getResults(by_metric=self.refit)
            self.best_params = dict(zip(self.grid.keys(), res_by.columns[res_by.loc['mean'].argmax()]))
            if self.verbose: 
                print('-----------------------------------------------------------')
                print('Fit final model')
                print('-----------------------------------------------------------')
                pprint(self.best_params)
            #self.best_model = self.model(**self.best_params).fit(X, y, X_val, y_val)
            self.best_model = self.model(**self.best_params).fit(X, y, X_val=X_val, y_val=y_val)
        return self

    def getResults(self, by_metric=False, aggregate=True):
        """
        Returns a dataframe with the results of the grid search cross validation. 
        Params:
            by_metric=False: If False no returns a dataframe containing all the metrics.
                             Else it has to be the name of ones of the metrics specified in the scoring dictionary.
                             This metric will be used to return a dataframe which is better to read.
            aggregate=True:  Wheather to aggregate the metrics to min, max, mean and std. 
                             Only used if by_metric=True.
        """
        results = pd.DataFrame(self.results)
        results.columns = pd.MultiIndex(results.columns.levels, results.columns.codes, names=self.grid.keys())
        if not by_metric: return results
        return self.__class__.results_by_metric(results, by_metric, aggregate)
        """
        def select_metric(c): return c[by_metric]
        res_by = results.map(select_metric)
        if not aggregate or by_metric == 'train_statistics': return res_by
        aggs = ['min', 'max', 'mean', 'std']
        return pd.concat([res_by, res_by.aggregate(aggs)])
        """

    def results_by_metric(results, by_metric, aggregate=True):
        """
        Params:
            results: Expects a dataframe with the results of the grid search cross validation. 
            by_metric:       Has to be the name of ones of the metrics specified in the scoring dictionary.
                             This metric will be used to return a dataframe which is better to read.
            aggregate=True:  Wheather to aggregate the metrics to min, max, mean and std. 
        """
        def select_metric(c): return c[by_metric]
        res_by = results.map(select_metric)
        if not aggregate or by_metric == 'train_statistics': return res_by
        aggs = ['min', 'max', 'mean', 'std']
        return pd.concat([res_by, res_by.aggregate(aggs)])

    """
    def save(self, filepath):
        \"""Save the GridSearch object as a pickle file to filepath.\"""
        with open(filepath, 'wb') as f:
            dump(self, f)
        return self

    def load(filepath):
        \"""Load a grid search object from a pickle file at filepath.\"""
        with open(filepath, 'rb') as f:
            grid_search = load(f)
            return grid_search
    """

    def __repr__(self):
        return f'{self.__class__.__name__}({self.model.__name__},\n{pformat(self.grid)},\nk_folds={self.k_folds})'
        