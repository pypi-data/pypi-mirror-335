import numpy as np
import pandas as pd

##################################################
# Regression metrics
##################################################
def mean_abolute_error(y_true, y_pred):
    """
    Returns the mean absolute error.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return np.mean(np.abs(y_true - y_pred))

def mean_squared_error(y_true, y_pred):
    """
    Returns the mean squared error.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return np.mean((y_true - y_pred)**2)

def root_mean_squared_error(y_true, y_pred):
    """
    Returns the root mean squared error.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return mean_squared_error(y_true, y_pred)**.5

def r2_score(y_true, y_pred):
    """
    Returns the R^2 score.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - y_true.mean())**2)


##################################################
# Classification metrics
##################################################
def accuracy(y_true, y_pred):
    """
    Returns the accuracy.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return np.mean(y_true == y_pred)

# Metrics by class
def precision_by_class(y_true, y_pred):
    """
    Computes the precision for each class individually.
    Params:
        y_true: ground truth
        y_pred: model prediction
    Returns (classes, metric): 
    A sorted list of classes with their corresponding score.
    """
    classes, res = __by_class(y_true, y_pred)
    return classes, [__save_divide(tp, (tp + fp)) for tp, fp, _, _ in zip(*res)]

def recall_by_class(y_true, y_pred):
    """
    Computes the recall for each class individually.
    Params:
        y_true: ground truth
        y_pred: model prediction
    Returns (classes, metric): 
    A sorted list of classes with their corresponding score.
    """
    classes, res = __by_class(y_true, y_pred)
    return classes, [__save_divide(tp, (tp + fn)) for tp, _, fn, _ in zip(*res)]

def f1_score_by_class(y_true, y_pred):
    """
    Computes the f1-score for each class individually.
    Params:
        y_true: ground truth
        y_pred: model prediction
    Returns (classes, metric): 
    A sorted list of classes with their corresponding score.
    """
    classes, prec = precision_by_class(y_true, y_pred)
    _, rec = recall_by_class(y_true, y_pred)
    return classes, [__save_divide((2*p*r), (p + r)) for p, r in zip(prec, rec)] #[(2*p*r) / (p + r) for p, r in zip(prec, rec)]

# Macro average metrics
def precision_macro_avg(y_true, y_pred):
    """
    Returns the macro average precision across classes.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return __macro_average(y_true, y_pred, precision_by_class)

def recall_macro_avg(y_true, y_pred):
    """
    Returns the macro average recall across classes.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return __macro_average(y_true, y_pred, recall_by_class)

def f1_macro_avg(y_true, y_pred):
    """
    Returns the macro average f1-score across classes.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    return __macro_average(y_true, y_pred, f1_score_by_class)
    

def confusion_matrix(y_true, y_pred):
    """
    Returns a dataframe that contains the confusion matrix.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    classes = np.sort(np.unique(y_true))
    def create_index(title): return pd.MultiIndex.from_tuples(zip([title]*len(classes), classes))
    return pd.DataFrame(
        [[np.sum((y_true == c1) & (y_pred == c2)) for c2 in classes] for c1 in classes], 
        columns=create_index('predicted'), 
        index=create_index('actual')
    )

def classification_report(y_true, y_pred):
    """
    Returns a dataframe that contains the a classification report.
    Params:
        y_true: ground truth
        y_pred: model prediction
    """
    classes, res = __by_class(y_true, y_pred)
    support = np.array([np.sum(y_true == c) for c in classes])
    prec = [__save_divide(tp, (tp + fp)) for tp, fp, _, _ in zip(*res)]
    rec = [__save_divide(tp, (tp + fn)) for tp, _, fn, _ in zip(*res)]
    report = pd.DataFrame({
        'precision':prec,
        'recall':rec,
        'f1-score':[__save_divide((2*p*r), (p + r)) for p, r in zip(prec, rec)],
        'support':support
    }, index=pd.Index(classes, name='class'))
    macro_avg = report.aggregate({c:'sum' if c == 'support' else 'mean' for c in report})
    weighted_avg = [(report[c] * support).sum() / len(y_true) for c in ['precision', 'recall', 'f1-score']] + [len(y_true)]
    report.loc['macro avg'] = macro_avg
    report.loc['weighted avg'] = weighted_avg
    report['support'] = report['support'].astype('uint')
    return report.round(3)


#####################################################
# Internal helpers
#####################################################
def __macro_average(y_true, y_pred, metric):
    """
    Can be used to create a function, that computes the macro average
    of a *_by_class metric. I.e. macro_average(precision_by_class) would
    compute the macro average of precision. 
    Macro average refers to the simple (not weighted) mean of the scores.
    """
    _, results = metric(y_true, y_pred)
    return np.mean(results)

def __by_class(y_true, y_pred):
    """Returns (tp, fp, fn, tn) by classes"""
    classes = np.unique(y_true)
    tp, fp, fn, tn = [], [], [], []
    for c in classes:
        yt = y_true == c
        yp = y_pred == c
        tp.append(np.sum(yt & yp))
        fp.append(np.sum(~yt & yp))
        fn.append(np.sum(yt & ~yp))
        tn.append(np.sum(~yt & ~yp))
    return classes, (tp, fp, fn, tn)

def __save_divide(x, y):
    return (x / y) if y != 0 else 0