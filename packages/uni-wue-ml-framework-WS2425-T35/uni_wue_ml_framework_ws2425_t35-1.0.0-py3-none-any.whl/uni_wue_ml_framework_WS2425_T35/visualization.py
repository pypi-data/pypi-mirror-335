import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
from pprint import pformat

from .model_selection import GridSearch

def savefig(path):
    if not path.lower().endswith('.png'): path += '.png'
    plt.tight_layout()
    plt.savefig(path, dpi=200, transparent=True)

#####################################################
# Training statistics
#####################################################
def plot_train_statistics(train_statistics, names=None, metric=None, figsize=None):
    """
    Create plots for visually comparing training statistics.
    Params:
    train_statistics: a list of train statistics of different models for comparison.
    names=None:       a list of model names, that there used for the legend. 
                      If None, models were named automatically.
    metric=None:      one or a list of the train statistic metrics that should be plotted.
                      If None all metrics are plotted on differend sublots.
    figsize=None:     The size of the figure as (width, height), if None will be inferred 
                      from the number of metrics to plot.
    """
    if metric is None: metrics = list(train_statistics[0].columns.levels[1])
    elif isinstance(metric, str): metrics = [metric]
    else: metrics = metric
    if figsize is None: figsize = (6, 2*len(metrics))
    fig,axes = plt.subplots(len(metrics), figsize=figsize)
    if len(metrics) == 1: axes = [axes]
    if names is None: names = [f'Model {i}' for i in range(len(train_statistics))]
    for metric, ax in zip(metrics, axes):
        for t,n,ls in zip(('val', 'train'), ('Validation', 'Train'), ('-', ':')):
            if len(train_statistics) > 1: ax.scatter(1,1, color=(0,0,0,0), label=n) # dummy plot for legend
            for i, s in enumerate(train_statistics):
                ax.plot(s.index, s[t][metric], c=f'C{i}', label=names[i] if len(train_statistics) > 1 else n, ls=ls)
            if ax == axes[0]: ax.legend(ncols=2)
        ax.set_ylabel(metric)
        if ax == axes[-1]: ax.set_xlabel('Epoch')
        else: ax.set_xticks([])
    plt.subplots_adjust(hspace=.05)


#####################################################
# Confusion matrix
#####################################################
def plot_confusion_matrix(confusion_matrix, title='Confusion matrix', figsize=None, ax=None):
    """
    Visualizes a of confusion matrix.  
    Params: 
        confusion_matrix: A confusion matrices as return from evaluation.plot_confusion_matrix.
        title='Confusion matrix': The plots title.
        figsize=None:     The figure size as (width, height). If None automatically infered from grid.
        hspace=05:        A factor used for vertical spacing between subplots.
        ax=None:          If None a new axis is created, otherwise ax is used for plotting.
    Returns the axis grid.
    """
    if figsize is None: figsize = (len(confusion_matrix), len(confusion_matrix)*5/6)
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(confusion_matrix.loc['actual', 'predicted'], annot=True, fmt='g', norm=LogNorm(), ax=ax)
    ax.set_ylabel('actual')
    ax.set_xlabel('predicted')
    if title: ax.set_title(title)

def plot_confusion_matrices(confusion_matrices, figsize=None, hspace=.05):
    """
    Visualizes a grid of confusion matrices.  
    Params: 
        classification_reports: A grid of accuracy- confusion matrices of shape (nrows, ncols).
                                Confusion matrices as return from evaluation.plot_confusion_matrix.
        figsize=None:           The figure size as (width, height). If None automatically infered from grid.
        hspace=05:              A factor used for vertical spacing between subplots.
    Returns the axis grid.
    """
    nrows, ncols = len(confusion_matrices), len(confusion_matrices[0])
    fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 3.4*nrows) if figsize is None else figsize)
    if axes.ndim == 1: axes = np.array([axes, ]) 
    for row, matr in zip(axes, confusion_matrices):
        for ax, matrix in zip(row, matr):
            plot_confusion_matrix(matrix, title=None, ax=ax)
            if ax not in axes[-1]: 
                ax.set_xticklabels([])
                ax.set_xlabel('')
            if ax not in axes[:,0]:
                ax.set_yticklabels([])
                ax.set_ylabel('')
    plt.subplots_adjust(hspace=hspace, wspace=.05)
    return axes

#####################################################
# Classification report 
#####################################################
def plot_classification_report(accuracy, classification_report, ax=None): 
    """
    Visualizes a classification report, 
    Params: 
        accuracy:              The models accuracy
        classification_report: A classification report as return from evaluation.classification_report.
        ax=None:               If None a new axis is created, otherwise ax is used for plotting.
    """
    if ax is None: fig,ax = plt.subplots() 
    classification_report.drop(columns='support').plot.bar(ax=ax)
    classes = classification_report.index[:-2]
    x_acc = -2/3
    ax.bar(x_acc, accuracy, 1/6, label='accuracy', color=f'C3') # {len(classes)}
    ax.set_xticks([x_acc] + list(range(len(classification_report.index))), 
                  ['accuracy'] + list(map(lambda v : f'{v[0]}\n{v[1]} instances',
                           zip(classes, classification_report['support'][:-2]))) + list(classification_report.index[-2:]))
    ax.set_xlim(-1)
    ax.set_ylim(0,1)
    ax.legend(loc='lower right', ncols=4)
    ax.set_xlabel('Metric')
    ax.set_ylabel('Score')
    return ax

def plot_classifications_reports(classification_reports, figsize=None, hspace=.05):
    """
    Visualizes a grid of classification reports, 
    Params: 
        classification_reports: A grid of accuracy- classification report tuples of shape (nrows, ncols, 2).
                                Classification report as return from evaluation.classification_report.
        figsize=None:           The figure size as (width, height). If None automatically infered from grid.
        hspace=05:              A factor used for vertical spacing between subplots.
    Returns the axis grid.
    """
    nrows, ncols = len(classification_reports), len(classification_reports[0])
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 3*nrows) if figsize is None else figsize)
    if axes.ndim == 1: axes = np.array([axes, ]) 
    for row, reports in zip(axes, classification_reports):
        for ax, (accuracy, report) in zip(row, reports):
            plot_classification_report(accuracy, report, ax=ax)
            if ax not in axes[-1]: 
                ax.set_xticklabels([])
                ax.set_xlabel('')
            if ax not in axes[:,0]:
                ax.set_yticklabels([])
                ax.set_ylabel('')
            ax.set_xlim(-1.1)
            ax.set_ylim(0,1)
            ax.legend(loc='lower right', ncols=2)
    plt.subplots_adjust(hspace=hspace, wspace=.05)
    return axes



#####################################################
# HPO CV grid search  
#####################################################
def plot_hpo_results_by(results, metric, drop_levels=[], title='Grid search mean $\\pm$ std', figsize=None, width_factor=1.1, ax=None):
    """
    Plot the results (mean +- std) of a hyperparemetr grid search.
    Params:
        results: the hyperparameter grid search results dataframe
        metric: the metric for which to plot the results.
        drop_levels=[]: hyperparameters that should not be used in x-ticks descriptions.
        title='Grid search mean $\\pm$ std': the figure title.
        figsize=None: the size of the figure. If None will be infered heuristically.
        width_factor=1.1: a factor used to controll the width of a figure (if not determined by figsize).
        ax=None: the axis used to plot. If None a new one is created.
    """
    results_by = GridSearch.results_by_metric(results, metric)
    results_by = results_by.T[results_by.index[-2:]] #.plot.bar()
    results_by.index = results_by.index.droplevel(drop_levels)

    if figsize is None: figsize = (__get_hpo_plot_width(results, width_factor, drop_levels), 2 + __get_max_str_len(results, drop_levels)/15)
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    results_by['mean'].plot.bar(yerr=results_by['std'], ax=ax)
    ax.set_xlabel(pformat(list(results_by.index.names), compact=True))
    ax.set_xticks(range(len(results_by)), list(map(lambda v : pformat(v, width=__PFORMAT_WIDTH), results_by.index.values)))
    ax.set_ylabel(metric)
    mi = (results_by['mean'] - results_by['std']).min()
    ma = (results_by['mean'] + results_by['std']).max()
    ax.set_ylim(mi - (ma - mi) / 10)
    if title: ax.set_title(title)

def plot_hpo_results(results, metrics, drop_levels=[], title='Grid search mean $\\pm$ std', figsize=None, width_factor=1.1, axes=None):
    """
    Plot the results (mean +- std) of a hyperparemetr grid search.
    Can be used th plot a selection of metrics.
    Params:
        results: the hyperparameter grid search results dataframe
        metrics: the metrics for which to plot the results.
        drop_levels=[]: hyperparameters that should not be used in x-ticks descriptions.
        title='Grid search mean $\\pm$ std': the figure title.
        figsize=None: the size of the figure. If None will be infered heuristically.
        width_factor=1.1: a factor used to controll the width of a figure (if not determined by figsize).
        ax=None: the axis used to plot. If None a new one is created.
    """
    if figsize is None: figsize = (
        __get_hpo_plot_width(results, width_factor, drop_levels),
        len(metrics) * 2 + __get_max_str_len(results, drop_levels)/15
    )
    if axes is None: fig, axes = plt.subplots(len(metrics), figsize=figsize)
    for metric, ax in zip(metrics, axes):
        plot_hpo_results_by(results, metric, title=None, drop_levels=drop_levels, width_factor=width_factor, ax=ax)
        if ax != axes[-1]: 
            ax.set_xticks([])
            ax.set_xlabel('')
    if title: plt.suptitle(title)
    plt.tight_layout()
    return axes 
"""
def plot_hpo_results_by(results, metric, drop_levels=[], title='Grid search mean $\\pm$ std', figsize=None, width_factor=1.1, ax=None):
    results_by = GridSearch.results_by_metric(results, metric)
    results_by = results_by.T[results_by.index[-2:]] #.plot.bar()
    results_by.index = results_by.index.droplevel(drop_levels)

    if figsize is None: figsize = (__get_hpo_plot_width(results, width_factor, drop_levels), 2 + __get_max_str_len(results, drop_levels)/15)
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    results_by['mean'].plot.bar(yerr=results_by['std'], ax=ax)
    ax.set_xlabel(pformat(list(results_by.index.names), compact=True))
    ax.set_xticks(range(len(results_by)), list(map(lambda v : pformat(v, width=__PFORMAT_WIDTH), results_by.index.values)))
    ax.set_ylabel(metric)
    ax.set_ylim(min(0, (results_by['mean'] - results_by['std']).min()), max(1, (results_by['mean'] + results_by['std']).max()))
    if title: ax.set_title(title)

def plot_hpo_results(results, metrics, drop_levels, title='Grid search mean $\\pm$ std', figsize=None, width_factor=1.1, axes=None):
    if figsize is None: figsize = (
        __get_hpo_plot_width(results, width_factor, drop_levels),
        len(metrics) * 2 + __get_max_str_len(results, drop_levels)/15
    )
    if axes is None: fig, axes = plt.subplots(len(metrics), figsize=figsize)
    for metric, ax in zip(metrics, axes):
        plot_hpo_results_by(results, metric, title=None, drop_levels=drop_levels, ax=ax)
        if ax != axes[-1]: 
            ax.set_xticks([])
            ax.set_xlabel('')
    if title: plt.suptitle(title)
    plt.tight_layout()
    return axes 
"""

#####################################################
# Internal helper
#####################################################
__PFORMAT_WIDTH = 40
def __get_hpo_plot_width(results, width_factor, drop_levels):
    n_params = len(results.columns.droplevel(drop_levels).levels)
    return width_factor * n_params * len(results.columns) / 5 # max_str_len / 60

def __get_max_str_len(results, drop_levels):
    return max(map(
        lambda params: 
        max(map(len, map(lambda v : pformat(v, width=__PFORMAT_WIDTH), params))), results.columns.droplevel(drop_levels).values
    ))
"""
def __get_hpo_plot_width(results, width_factor, drop_levels):
    return width_factor * len(results.columns.droplevel(drop_levels).levels) * len(results) / 5# max_str_len / 60

def __get_max_str_len(results, drop_levels):
    return max(map(
        lambda params: 
        max(map(len, map(lambda v : pformat(v, width=__PFORMAT_WIDTH), params))), results.columns.droplevel(drop_levels).values
    ))
"""