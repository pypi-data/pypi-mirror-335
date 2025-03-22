import pandas as pd
import matplotlib.pyplot as plt
from json import dump, dumps, load, loads
import os

from .model.neural_network import NeuralNetwork
from .preprocessing import Pipeline
from .model_selection import GridSearch
#import visualization 
from .visualization import *
#import evaluation
from .evaluation import accuracy, confusion_matrix, classification_report

#####################################################
# Save and evaluate a model or Pipeline object
#####################################################
def save_classification_model(model, X_test, y_test, metadata, path):
    """
    Save and evaluate a model or Pipeline object.
    Params:
        model:    the model or Pipeline object.
        X_test:   test train set.
        y_test:   test ground truth.
        metadata: additional data that will be stored in the JSON file.
        path:     the path to save to model.
    """
    os.makedirs(path, exist_ok=True)
    filepath = __path_builder(path)
    os.makedirs(filepath('figures'), exist_ok=True)
    
    y_pred = model.predict(X_test)
    
    # accuracy
    acc = accuracy(y_test, y_pred)
    
    # confusion matrix
    matrix = confusion_matrix(y_test, y_pred)
    matrix.to_csv(filepath('confusion_matrix.csv'))
    plot_confusion_matrix(matrix)
    savefig(filepath('figures', 'confusion_matrix'))
    
    # classification report
    report = classification_report(y_test, y_pred)
    report.to_csv(filepath('classification_report.csv'))
    plot_classification_report(acc, report)
    savefig(filepath('figures', 'classification_report'))

    # Train statistics
    m = model.model if isinstance(model, Pipeline) else model
    train_statistics = __train_statistics_to_df(m.statistics)
    plot_train_statistics([train_statistics])
    savefig(filepath('figures', 'train_statistics'))
    
    # others
    result = {
        'accuracy':acc,
        'classification_report':report.to_dict(),
        'train_statistics':m.statistics,
        'test_data':{'y_true':y_test.tolist(), 'y_pred':y_pred.tolist(), 'y_pred_proba':model.predict_proba(X_test).tolist()},
        'metadata':metadata
    }
    with open(filepath('evaluation.json'),'w') as f:
        dump(result, f)
    
    # save model
    model.save(filepath('model.pkl'))


def load_classification_model(path):
    """
    Load the classification evaluation data and model.
    Params: path: the path to the data folder.
    Returns:
        accuracy, 
        confusion_matrix, 
        classification_report, 
        train_statistics, 
        test_data,
        metadata,
        model
    """
    filepath = __path_builder(path)

    # load data file
    with open(filepath('evaluation.json'),'r') as f:
        result = load(f)

    # classification_report
    report = pd.DataFrame(result['classification_report'])
    
    # confusion matrix
    matrix = pd.read_csv(filepath('confusion_matrix.csv'), index_col=[0,1], header=[0,1])
    
    # train statistics
    train_statistics = __train_statistics_to_df(result['train_statistics'])
    
    # model
    model = NeuralNetwork.load(filepath('model.pkl')) # can be an instance of NeuralNetwork or Pipeline

    # return 
    return result['accuracy'], matrix, report, train_statistics, result['test_data'], result['metadata'], model

#####################################################
# Save and evaluate a GridSearch object
#####################################################
def save_classification_grid_search(grid_search, X_test, y_test, path, drop_levels=None, metadata=None):
    """
    Save and evaluate a GridSearch object:
        grid_search: the grid search object, an instance of GridSearch.
        X_test:      test train set.
        y_test:      test ground truth.
        path:        the path to save to model.
        drop_levels: Parameter choices that are not included in HPO result plots.
                     If None ['model', 'task', 'verbose', 'random_state'] are excluded.
        metadata:    additional data that will be stored in the JSON file.
    """
    os.makedirs(path, exist_ok=True)
    filepath = __path_builder(path)
    os.makedirs(filepath('figures'), exist_ok=True)
    
    # grid search results table
    results = grid_search.getResults()
    results.map(dumps).to_csv(filepath('hpo_cv_grid_search.csv'))
    grid_search.save(filepath('hpo_cv_grid_search.pkl'))

    # metadata including best hyperparameters
    if metadata is None:
        metadata = {}
    metadata.update({'hyperparameter':dict(zip(grid_search.best_params, map(str, grid_search.best_params.values())))})

    # plots
    if drop_levels is None: drop_levels = [l for l in ['model', 'task', 'verbose', 'random_state'] if l in results.columns.names]
    for metric in grid_search.scoring:
        plot_hpo_results_by(results, metric, drop_levels=drop_levels)
        plt.tight_layout()
        savefig(filepath('figures', f'hpo_results_{metric}'))
    plot_hpo_results(results, grid_search.scoring.keys(), drop_levels=drop_levels);
    savefig(filepath('figures', f'hpo_results'))

    save_classification_model(model=grid_search.best_model, X_test=X_test, y_test=y_test, metadata=metadata, path=path)

def load_classification_grid_search(path):
    """
    Load the classification evaluation data and grid search instance.
    Params: path: the path to the data folder.
    Returns:
        accuracy, 
        confusion_matrix, 
        classification_report, 
        train_statistics, 
        test_data,
        metadata,
        model, 
        hpo_results,
        grid_search
    """
    filepath = __path_builder(path)
    acc, matrix, report, train_statistics, test_data, metadata, model = load_classification_model(path=path)
    hpo_results = pd.read_csv(filepath('hpo_cv_grid_search.csv'), index_col=0, header=list(range(len(metadata['hyperparameter'])))).map(loads)
    grid_search = GridSearch.load(filepath('hpo_cv_grid_search.pkl'))
    return acc, matrix, report, train_statistics, test_data, metadata, model, hpo_results, grid_search

#####################################################
# Internal helpers
#####################################################
def __path_builder(path):
    def join(*suffixes):
        return os.path.join(path,*suffixes)
    return join 

def __train_statistics_to_df(statistics):
    statistics = pd.DataFrame({(t, m):statistics[t][m]
                               for t in statistics
                               for m in statistics[t] if t != 'epoch'},
                              index=pd.Index(statistics['epoch'], name='epoch'))
    statistics.columns = pd.MultiIndex(statistics.columns.levels, statistics.columns.codes, names=('Set', 'Metric'))
    return statistics