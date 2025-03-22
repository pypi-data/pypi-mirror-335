# Machine Learning Framework

Welcome to our Machine Learning Package! This library is designed to simplify and accelerate the development of machine learning models. 

API inspired by [scikit-learn](https://scikit-learn.org/stable/): Intuitive functions and classes for model training, evaluation, and deployment.


This package provides a comprehensive suite of tools for building, evaluating, and visualizing machine learning models. It is organized into several modules, each serving a specific purpose in the machine learning workflow. Key modules include:

- **`model`**: Implements neural networks, activation functions, cost functions, and optimizers.
- **`model_selection`**: Provides train-test splitting and hyperparameter grid search.
- **`preprocessing`**: Includes pipelines, feature selection, and PCA for data preparation.
- **`evaluation`**: Offers metrics for regression and classification model performance.
- **`visualization`**: Tools for plotting training statistics, confusion matrices, and classification reports.
- **`saving`**: Functions to save and load models and grid search results.

Furthermore it provides an example notebook, with examples how to use this package: `NeuralNetwork.ipynb`.

## The `model` module
* `neural_network` including the `NeuralNetwork` class (a fully connected feed forward network aka. a multi layer perceptron)
* `activation_function` offers a collection of activation functions, including
    * `sigmoid`: Sigmoid activation function.
    * `relu`: ReLu activation function.
    * `tanh`: Tangens hyperbolicus activation function.
* `cost_function` with two cost functions:
    * `cross_entropy`: Cross entropy loss function.
    * `mse`: Mean squared error loss function.
    * and `softmax`.
* `layer` including the `Layer` class, which is an internal class used to represent a layer.
* `optimzer` including a base class for different optimizers and an implementation for gradient descent: `GradientDescent`.

### `NeuralNetwork`

The `NeuralNetwork` class is a custom implementation of a feed-forward neural network (multi-layer perceptron) designed for both regression and classification tasks. Here's a breakdown of its components, hyperparameters, and functions:

Key Features
- **Flexibility**: Supports both regression and classification tasks with customizable layers and functions.
- **Early Stopping**: Prevents overfitting by stopping training when validation performance stops improving.
- **Statistics Tracking**: Monitors training and validation performance using specified metrics.
- **Reproducibility**: Allows setting a random seed for consistent results across runs.

Hyperparameters

- **`hidden_layer_sizes`**: A list specifying the number of neurons in each hidden layer.
- **`activation`**: The activation function to use in the hidden layers (as implemented in the `activation_function` module e.g., `sigmoid`, `relu`).
- **`loss_func`**: The loss function to optimize during training (as implemented in the `cost_function` module e.g., `cross_entropy`, `mse`).
- **`task`**: Specifies whether the task is `'regression'` or `'classification'`.
- **`epochs`**: The number of complete passes through the training dataset.
- **`learning_rate`**: The step size during optimization to update the model parameters.
- **`batch_size`**: The number of samples per gradient update. If `None`, the entire dataset is used.
- **`early_stopping`**: Stops training if the validation loss doesn't improve for a specified number of epochs.
- **`optimizer`**: The optimization algorithm used to update the network's weights (e.g., `GradientDescent`).
- **`train_statistic_metrics`**: Metrics to track during training (e.g., `RMSE`, `accuracy`).
- **`random_state`**: Seed for random number generation to ensure reproducibility.
- **`verbose`**: Controls the amount of information printed during training.

Functions

- **`__init__`**: Initializes the neural network with specified hyperparameters.
- **`predict_raw`**: Performs a forward pass through the network, returning raw predictions.
- **`predict_proba`**: Returns probabilities for classification tasks after applying softmax.
- **`predict`**: Returns final predictions. For regression, it returns raw values; for classification, it returns class labels.
- **`fit`**: Trains the neural network on the provided data. It supports early stopping and tracks training statistics if a validation set is provided. Parameters:
    * `X`: A NumPy array of shape (n_samples, n_features) containing the training features.
    * `y`: A NumPy array of shape (n_samples,) containing the target values for the training data.
    * `X_val=None`: An optional NumPy array of shape (n_val_samples, n_features) containing validation features.
    * `y_val=None`: An optional NumPy array of shape (n_val_samples,) containing target values for the validation data.

    If X_val and y_val are provided, the method calculates and tracks validation metrics to monitor performance and enable early stopping.

- **`plot_statistics`**: Plots training and validation statistics, such as loss and metrics over epochs.
- **`__repr__`**: Provides a string representation of the neural network, including its configuration and hyperparameters.

Example of application

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

from ml_framework.model_selection import train_test_split

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

# Initialize the neural network
nn = NeuralNetwork(
    hidden_layer_sizes=[16, 8],
    activation=relu,
    loss_func=cross_entropy,
    task='classification',
    epochs=50,
    learning_rate=0.01,
    batch_size=16,
    early_stopping=5,
    verbose=1
)

# Train the neural network
nn.fit(X_train, y_train, X_val=X_val, y_val=y_val)

# Make predictions on the validation set
predictions = nn.predict(X_val)
predict_probabilites = nn.predict_proba(X_val)
```


## The `model_selection` module
* Train test split functionality: `train_test_split`.
* The `GridSearch` class to perform cross validated hyperparameter grid search for HPO.

### Train test split

The `train_test_split` function is designed to split datasets into training and testing subsets, similar to the implementation found in scikit-learn. Here's a brief explanation of its usage and parameters:

- **Function Signature**:
  ```python
  def train_test_split(*args, test_size, random_state=None):
  ```

- **Parameters**:
  - `*args`: Variable-length argument list that allows the function to accept multiple datasets (e.g., features `X` and target `y`).
  - `test_size`: The proportion of the dataset to include in the test split (e.g., `0.33` means 33% of the data will be used for testing).
  - `random_state`: An optional parameter to set the seed for the random number generator, ensuring reproducibility of the split.

- **Usage**:
  ```python
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
  ```
  - This line of code splits the feature dataset `X` and the target dataset `y` into training and testing subsets, with 33% of the data allocated to the test set.


### HPO cross validated grid search 


The `GridSearch` class is designed to perform hyperparameter tuning using a grid search with k-fold cross-validation. It systematically works through the combinations of hyperparameters, evaluating each combination using a specified metric. Here's a detailed explanation of its functionality, methods, and usage:

#### Functionality

- **Hyperparameter Tuning**: Automatically searches through a specified grid of hyperparameters to find the best combination for a given model.
- **Cross-Validation**: Uses k-fold cross-validation to evaluate each hyperparameter combination, ensuring robust performance estimation.
- **Scoring**: Allows for multiple evaluation metrics to assess model performance.
- **Refitting**: Optionally refits the model on the entire dataset using the best hyperparameters found during the search.
- **Results Analysis**: The `getResults` method allows for easy analysis of grid search results, helping to identify the best hyperparameters.

### Methods

* **`__init__`**: Initializes the `GridSearch` object with the model, hyperparameter grid, number of folds, scoring metrics, and other settings.
* **`fit`**:
   - Performs the grid search by iterating over all hyperparameter combinations.
   - Splits the data into k-folds and evaluates each combination using cross-validation.
   - Optionally refits the model with the best hyperparameters on the entire dataset.
* **`getResults`**:
   - Returns the results of the grid search as a DataFrame.
   - Allows filtering results by a specific metric and aggregating statistics (min, max, mean, std).
* **`results_by_metric`**: A static method that processes the results DataFrame to extract and aggregate metrics for better readability.
* **`__repr__`**: Provides a string representation of the `GridSearch` object, including the model and hyperparameter grid.

#### Usage Example

Suppose you want to tune the hyperparameters of a neural network for a classification task using the Iris dataset.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

from ml_framework.model_selection import train_test_split

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

# Define the model and hyperparameter grid
model = NeuralNetwork
grid = {
    'hidden_layer_sizes': [[16, 8], [32, 16]],
    'learning_rate': [0.01, 0.001],
    'batch_size': [16, 32]
}

# Define scoring metrics
scoring = {
    'accuracy': accuracy_score
}

# Initialize and perform grid search
grid_search = GridSearch(
    model=model,
    grid=grid,
    k_folds=5,
    scoring=scoring,
    refit='accuracy',
    random_state=42,
    verbose=1
)

grid_search.fit(X_train, y_train, X_val=X_val, y_val=y_val)

# Get the results
results_df = grid_search.getResults('accuracy')
print(results_df)

# Access the best model
best_model = grid_search.best_model

# Evaluate the best model on the validation set
predictions = best_model.predict(X_val)
```


## The `preprocessing` module
Includes several classes for preprocessing: 
* `Pipeline`: For the creation of a preprocessing pipeline of a sequence of preprocessing transformer.
* `FeatureSelection`: A preprocessing transformer for feature selection.
* `PCA` (Principal component analysis): A preprocessing transformer for dimensionality reduction.

### `Pipeline`

The `Pipeline` class is designed to streamline the process of applying a sequence of preprocessing steps to data before fitting a model or making predictions. This is particularly useful in machine learning workflows where data needs to be transformed in multiple ways before being fed into a model. 

#### Functionality

- **Sequential Processing**: Applies a series of preprocessing steps in a specified order.
- **Model Integration / Consistency**: Fits a model on the preprocessed data and allows for predictions using the same preprocessing steps.
- **Modularity / Encapsulation**: Encapsulates the entire preprocessing and modeling workflow, making it easier to manage and apply consistently.
- **Efficiency**: Streamlines the workflow by encapsulating the entire preprocessing and modeling process.

This class is particularly useful in complex machine learning workflows where data needs to undergo multiple transformations before being fed into a model.

#### Methods

* **`__init__`**:
   - Initializes the `Pipeline` with a list of preprocessing steps and a model.
   - **Parameters**:
     - `steps`: A list of preprocessor objects, each implementing `fit_transform` and `transform` methods.
     - `model`: A model class that will be instantiated with any additional keyword arguments (`kwargs`).
* **`fit`**:
   - Applies the preprocessing steps to the input data `X` and fits the model on the transformed data against `y`.
   - **Parameters**:
     - `X`: Input features.
     - `y`: Target values.
     - `X_val`, `y_val`: Optional validation data.
   - **Process**:
     - Each preprocessing step's `fit_transform` method is called on `X`.
     - The model is fitted on the transformed data.
* **`predict`**:
   - Applies the preprocessing steps to the input data `X` and returns the model's predictions.
   - **Process**:
     - Each preprocessing step's `transform` method is called on `X`.
     - The model's `predict` method is called on the transformed data.
* **`predict_proba`**:
   - Similar to `predict`, but returns probabilities for classification tasks.
* **`transform`**:
   - Applies the preprocessing steps to the input data `X` and returns the transformed data.
   - Useful for obtaining the transformed data without making predictions.
* **`__repr__`**:
   - Provides a string representation of the `Pipeline`, including the preprocessing steps and the model.

#### Usage Example

Suppose you want to build a pipeline that standardizes the features and then applies PCA before fitting a neural network to the Iris dataset.

```python
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

from ml_framework.preprocessing import PCA
from ml_framework.model_selection import train_test_split

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the preprocessing steps
steps = [
    StandardScaler(),  # Standardize features
    PCA(n_components=2)  # Apply PCA to reduce dimensionality
]

# Define the model
model = NeuralNetwork

# Initialize the pipeline
pipeline = Pipeline(
    steps=steps,
    model=model,
    hidden_layer_sizes=[16, 8],
    activation=relu,
    loss_func=cross_entropy,
    task='classification',
    epochs=50,
    learning_rate=0.01,
    batch_size=16,
    early_stopping=5,
    verbose=1
)

# Fit the pipeline
pipeline.fit(X_train, y_train, X_val=X_val, y_val=y_val)

# Make predictions
predictions = pipeline.predict(X_val)
```

### `FeatureSelection`

The `FeatureSelection` class is a simple transformer designed to select specific features (columns) from a dataset using a boolean mask. This is useful in machine learning pipelines where you want to apply feature selection before training a model. Here's a detailed explanation of its functionality, methods, and usage:

#### Functionality

- **Feature Selection**: Selects specific columns from a dataset based on a predefined mask.
- **Transformer**: Acts as a transformer in a machine learning pipeline, implementing `transform` and `fit_transform` methods.
- **Mask-Based**: Uses a boolean mask to determine which features to select.

#### Methods

1. **`__init__`**:
   - Initializes the `FeatureSelection` object with a boolean mask.
   - **Parameters**:
     - `mask`: A boolean array where `True` indicates that the corresponding feature should be selected.

2. **`transform`**:
   - Applies the mask to the input data `X` and returns the selected features.
   - **Parameters**:
     - `X`: Input data as a NumPy array.
   - **Returns**: A NumPy array containing only the selected features.

3. **`fit_transform`**:
   - In this implementation, it simply calls the `transform` method since there is no fitting process involved.
   - **Parameters**:
     - `X`: Input data as a NumPy array.
   - **Returns**: A NumPy array containing only the selected features.

4. **`__repr__`**:
   - Provides a string representation of the `FeatureSelection` object, displaying the class name.

#### Usage Example

Suppose you have a dataset and you want to select only the first and third features for training a model.

```python
import numpy as np

# Sample dataset
X = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
])

# Define a mask to select the first and third features
mask = np.array([True, False, True, False])

# Initialize the FeatureSelection transformer
feature_selector = FeatureSelection(mask=mask)

# Apply feature selection
X_selected = feature_selector.fit_transform(X)

print("Original Data:\n", X)
print("Selected Features:\n", X_selected)
```

### `PCA`

The `PCA` class implements Principal Component Analysis (PCA), a technique used for dimensionality reduction while preserving as much variability as possible in the data. Here's a detailed explanation of its functionality, methods, and usage:

#### Functionality

- **Dimensionality Reduction**: Reduces the number of features in a dataset by transforming it into a new set of variables (principal components) that capture the most variance.
- **Feature Transformation**: Transforms the original features into a new space defined by the principal components.

#### Methods

1. **`__init__`**:
   - Initializes the `PCA` object with the desired number of principal components.
   - **Parameters**:
     - `n_components`: The number of principal components to compute.

2. **`fit`**:
   - Computes the mean, covariance matrix, eigenvalues, and eigenvectors of the input data `X`.
   - The eigenvectors corresponding to the largest eigenvalues form the principal components.
   - **Parameters**:
     - `X`: Input data as a NumPy array.
   - **Process**:
     - Centers the data by subtracting the mean.
     - Computes the covariance matrix.
     - Computes eigenvalues and eigenvectors of the covariance matrix.
     - Selects the top `n_components` eigenvectors as the principal components.

3. **`transform`**:
   - Projects the input data `X` onto the principal components, reducing its dimensionality.
   - **Parameters**:
     - `X`: Input data as a NumPy array.
   - **Returns**: Transformed data with reduced dimensions.

4. **`fit_transform`**:
   - Combines the `fit` and `transform` methods into a single step for efficiency.
   - **Parameters**:
     - `X`: Input data as a NumPy array.
   - **Returns**: Transformed data with reduced dimensions.

5. **`__repr__`**:
   - Provides a string representation of the `PCA` object, displaying the number of components.

#### Usage Example

Suppose you have a dataset and you want to reduce its dimensionality to 2 components using PCA.

```python
import numpy as np

# Sample dataset
X = np.array([
    [2.5, 2.4],
    [0.5, 0.7],
    [2.2, 2.9],
    [1.9, 2.2],
    [3.1, 3.0],
    [2.3, 2.7],
    [2, 1.6],
    [1, 1.1],
    [1.5, 1.6],
    [1.1, 0.9]
])

# Initialize PCA with 2 components
pca = PCA(n_components=2)

# Fit and transform the data
X_transformed = pca.fit_transform(X)

print("Original Data:\n", X)
print("Transformed Data:\n", X_transformed)
```

### Key Points

- **Variance Capture**: The principal components capture the directions of maximum variance in the data.
- **Dimensionality Reduction**: Useful for visualizing high-dimensional data and reducing computational complexity.
- **Data Centering**: The data is centered by subtracting the mean before computing the covariance matrix.

This class is particularly useful in preprocessing steps for machine learning pipelines, where reducing the dimensionality of the data can improve model performance and efficiency.


## The `evaluation` module
A module with different functions for model evaluation.
* Regression metrics: 
    * `mean_abolute_error`: Computes the mean absolute error (MAE).
    * `mean_squared_error`: Computes the mean squared error  (MSE).
    * `root_mean_squared_error`: Computes the root mean squared error (RMSE).
    * `r2_score`:  Computes the $R^2$ score.
* Classification metrics:
    * `accuracy`: Computes the accuracy:
    * `precision_by_class`: Computes the precision for each class individually.
    * `recall_by_class`: Computes the recall for each class individually.
    * `f1_score_by_class`: Computes the f1-score for each class individually.
    * `precision_macro_avg`: Computes the macro average precision across classes.
    * `recall_macro_avg`: Computes macro average recall across classes.
    * `f1_macro_avg`: Computes macro average f1-score across classes.
    * `confusion_matrix`: Returns a dataframe that contains the confusion matrix.
    * `classification_report`: Returns a dataframe that contains the a classification report. The report includes precision, recall F1-score (class-wise and macro average) and support.

All the functions expect the following parameters:
Params:
* `y_true`: ground truth
* `y_pred`: model prediction

Usage:
```python
from ml_framework import evaluation

accuracy = evaluation.accuracy(y_true, y_pred)
report = evaluation.classification_report(y_true, y_pred)
```

## The `visualization` module
Includes several functions for visualization of model performance and training statsistics.
* `savefig`: Saves a matplotlib figure to the specified filepath.
* `plot_train_statistics`: Creates plots for visually comparing training statistics.
* `plot_confusion_matrix`: Visualizes a of confusion matrix.  
* `plot_confusion_matrices`: Visualizes a grid of confusion matrices.  
* `plot_classification_report`: Visualizes a classification report.
* `plot_classifications_reports`: Visualizes a grid of classification reports.
* `plot_hpo_results_by`: Plot the results (mean $\pm$ std) of a hyperparemetr grid search. Used for the results regarding a single metric.
* `plot_hpo_results`:  Plot the results (mean $\pm$ std) of a hyperparemetr grid search. Can be used th plot a selection of metrics.


## The `saving` module
Includes functions to evaluate and save and load models and grid searches.

`PATH` is a path to a folder, where all the saved data should be stored including the model / hyperparameter grid search object.
* `save_classification_model`:  Save and evaluate a model or Pipeline object.
    * Usage:
        ```python 
        save_classification_model(model, Xnew, ynew, path=PATH)
        ```
* `load_classification_model`: Load the classification evaluation data and model.
    * Usage:
        ```python
        (accuracy, confusion_matrix, classification_report, 
        train_statistics, test_data, metadata, model) = load_classification_model(PATH)
        ```
* `save_classification_grid_search`: Save and evaluate a GridSearch object:
    * Usage:
        ```python 
        save_classification_grid_search(grid_search, Xnew, ynew, path=PATH)
        ```
* `load_classification_grid_search`: Load the data of classification evaluation and grid search instance.
    * Usage:
        ```python
        (accuracy, confusion_matrix, classification_report, train_statistics, 
        test_data, metadata, model, hpo_results, grid_search) = load_classification_grid_search(PATH)
        ```