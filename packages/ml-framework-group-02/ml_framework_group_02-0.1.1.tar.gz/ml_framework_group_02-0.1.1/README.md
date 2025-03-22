# ML Framework
## Overview

This custom Machine Learning (ML) framework is designed to support the creation and training of neural networks for general classification tasks. Inspired by popular frameworks like PyTorch and Keras, this package allows you to easily build, train, and test neural networks using customizable layers, cost functions, and optimizers.

The framework offers the flexibility to adjust hyperparameters such as the number of layers, neurons per layer, learning rate and much more. With an input of multiple batches it uses vectorized calculations for fast training. Also the different functions are written and used in a generalized way so own functions e.g. an own optimizer could be used in the framework. It provides k-fold cross validation for efficient learning on smaller datasets and with early stopping it takes the efficiency even further.

## Core Components & Features

Our framework abstracts general machine learning functionality from project‐specific code and includes the following modules and features:

- **Neural Network Layers:**  
  - Customizable layer objects for constructing feedforward neural networks.

- **Activation Functions:**  
  - Sigmoid  
  - Tanh  
  - LeakyReLU  
  - Softmax

- **Bias Initialization Strategies:**  
  - Constant initialization  
  - Random initialization

- **Weight Initialization Strategies:**  
  - Random initialization  
  - Xavier initialization  
  - He initialization

- **Optimizers:**  
  - Gradient Descent  
  - Momentum Gradient Descent  
  - Adam

- **Loss Functions:**  
  - Mean Squared Error  
  - Cross Entropy (with Softmax)

- **Accuracy Metrics:**  
  - Accuracy  
  - Precision  
  - Recall  
  - F1 Score

---

### Usage Example

Below is an example of how to create and customize a neural network using our framework:

```python
import numpy as np
from ml_framework import*

# Define network dimensions
input_size = 784       # Example: MNIST images (28x28 flattened)
hidden_size = 128      # Number of neurons in the hidden layer
output_size = 10       # Number of classes (digits 0-9)

# Create layers with custom weight and bias initializations
layer1 = Layer(input_size, hidden_size, weight_initializer=Xavier(), bias_initializer=Constant(val = 0.01))
activation1 = Sigmoid()   
layer2 = Layer(hidden_size, output_size, weight_initializer=He(), bias_initializer=Random(min = -0.01, max = 0.01))
activation2 = Softmax()   

stack = [layer1, activation1, layer2, activation2]


model = Classifier(
    stack,
    optimizer_function=Adam(learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8),         
    loss_function=CrossEntropy(),        
    accuracy_functions=[Accuracy(), Precision(), Recall(), F1Score()]  
)

model.train(
    epochs=50,
    input=X_train,
    labels=y_train,
    folds=5,
    stop_patience=10,
    log_epochs=5,
    history_epochs=5
)

# Predict using the trained network on new data (X_test)
predictions = model.predict(X_test)
predicted_labels = model.predict_label(X_test)
```

---

This example demonstrates how you can customize the network architecture, choose different initializations, optimizers, and loss functions, and train your model using our ML framework—all while keeping the machine learning logic completely separate from project-specific code. For a more in-depth usage example please refer to our notebook `ml_framework_group_02/examples/simple-classification.ipynb`. 

---

For more efficient training you can also apply PCA in the preprocessing step:

## PCA (O2)
# PCA Class Usage Guide

The `PCA` class implements Principal Component Analysis (PCA), a technique used for dimensionality reduction. Below is a guide on how to use the individual functions of the `PCA` class.

## Initialization

To create an instance of the `PCA` class, you need to specify the number of principal components you want to keep.

```python
pca = PCA(n_components=2)
```

## Fitting the Model

The `fit` method computes the mean, covariance matrix, eigenvalues, and eigenvectors of the input data `X`.

```python
pca.fit(X)
```

- `X`: Input data matrix of shape (n_samples, n_features).

## Transforming the Data

The `transform` method projects the input data `X` onto the principal components.

```python
X_transformed = pca.transform(X)
```

- `X`: Input data matrix of shape (n_samples, n_features).
- Returns: Transformed data matrix of shape (n_samples, n_components).

## Fitting and Transforming in One Step

The `fitTransform` method combines fitting the model and transforming the data in one step.

```python
X_transformed = pca.fitTransform(X)
```

- `X`: Input data matrix of shape (n_samples, n_features).
- Returns: Transformed data matrix of shape (n_samples, n_components).

## Inverse Transformation

The `inverseTransform` method reconstructs the original data from the transformed data.

```python
X_reconstructed = pca.inverseTransform(X_transformed)
```

- `X_transformed`: Transformed data matrix of shape (n_samples, n_components).
- Returns: Reconstructed data matrix of shape (n_samples, n_features).

## Explained Variance

The `getExplainedVariance` method returns the amount of variance explained by each of the selected principal components.

```python
explained_variance = pca.getExplainedVariance()
```

- Returns: Array of shape (n_components,) containing the explained variance.

## Explained Variance Ratio

The `getExplainedVarianceRatio` method returns the ratio of the variance explained by each of the selected principal components.

```python
explained_variance_ratio = pca.getExplainedVarianceRatio()
```

- Returns: Array of shape (n_components,) containing the explained variance ratio.

## Example Usage

Here is an example of how to use the `PCA` class:

```python
import numpy as np

# Create a PCA instance with 2 components
pca = PCA(n_components=2)

# Generate some sample data
X = np.random.rand(100, 5)

# Fit the PCA model to the data
pca.fit(X)

# Transform the data
X_transformed = pca.transform(X)

# Fit and transform the data in one step
X_transformed = pca.fitTransform(X)

# Inverse transform the data
X_reconstructed = pca.inverseTransform(X_transformed)

# Get the explained variance
explained_variance = pca.getExplainedVariance()

# Get the explained variance ratio
explained_variance_ratio = pca.getExplainedVarianceRatio()
```
Finally one can display various metrics to analyze the performance of the model in depth as well as compare multiple models against each other:

## Visualization Module (O1.1)

This module meets the following requirements for visualization (5 points):

- [x] **Multiple Model Comparison:**  
  The framework implements functions such as `plot_metric_across_models` that allow you to visually compare metrics from multiple trained models. You can load the saved metrics data (e.g., loss history, accuracy metrics, confusion matrices) from different models to generate combined visualizations.

- [x] **Visualizing Key Metrics:**  
  It visualizes crucial metrics including:
  - **Loss:** Plots of loss over epochs (raw, smoothed, and training vs validation).
  - **Accuracy & F1 Score:** Time-series plots that show training accuracy, precision, recall, and F1 score.
  - **Confusion Matrices:** Graphs generated via `plot_confusion_matrix` to evaluate the performance on classification tasks.

- [x] **Saving Visualizations:**  
  All generated plots are saved automatically to designated directories (e.g., `visualizations/`, `saved_metrics/`). This ensures reproducibility and later reference.

- [x] **Storing Raw Data:**  
  The framework not only saves plots as images but also stores the raw data used to create these graphs (e.g., loss and accuracy histories saved in json files). This facilitates further analysis or re-plotting without retraining models.

- [x] **Combined Visualizations:**  
  Functions like `plot_metric_across_models` allow you to load data from multiple models (by reading the saved JSON and pickle files) and produce combined plots to compare metrics such as accuracy, F1 score, or even confusion matrices.

### Key Functions

- **`generate_model_metrics(model, X_test, y_test, model_name, save_dir='saved_metrics')`**  
  - **Purpose:** Evaluates a model on test data and extracts performance metrics.
  - **Functionality:**  
    - Tests the model to obtain final loss, accuracy metrics, and confusion matrix.
    - Retrieves training histories (loss and accuracy) using model methods.
    - Saves the computed metrics as a JSON file.
    - Calls `visualize_final_accuracies` to display a bar chart of test metrics.
  
  **Usage Example:**
  ```python
  metrics = generate_model_metrics(trained_model, X_test, y_test, "my_model")
  ```
  
- **`visualize_final_accuracies(final_accuracies)`**  
  - **Purpose:** Generates and displays a bar chart of final test metrics (accuracy, precision, recall, F1 score).
  - **Output:** The plot is displayed and saved, ensuring that visualizations are stored for later reference.

- **`plot_metric_across_models(metric_key, models_metrics, model_names, ...)`**  
  - **Purpose:** Compares a specified metric (e.g., loss, accuracy, or F1 score) across multiple models.
  - **Functionality:**  
    - Handles both time-series plots and confusion matrices.
    - Loads raw data from saved metrics files to generate combined visualizations.
    - Saves the resulting plots to a file.
  

  **Usage Example:**

  ```python
  plot_metric_across_models("training_accuracy", [metrics1, metrics2], ["Model 1", "Model 2"])
  ```

Other options are: 

the following:
    - `"final_loss"`,
    - `"final_accuracies"`, 
    - `"confusion_matrix"`, 
    - `"loss_history"`, 
    - `"training_accuracy_metrics"`,
    - `"training_precision"`, 
    - `"training_recall"`, 
    - `"training_f1"`, 
    - `"training_vs_validation_loss"`



### Additional Visualization Options

- **ROC & Precision-Recall Curves:**  
  - **`plot_roc_curves(y_score, y_true, classes, output_dir='visualizations')`**  
    - **Purpose:** Plot Receiver Operating Characteristic (ROC) curves for each class, enabling comparisons of true positive versus false positive rates.  
  - **`plot_precision_recall_curves(y_true, y_score, classes, output_dir='visualizations')`**  
    - **Purpose:** Plot Precision-Recall curves for each class, which can be used to evaluate models under different thresholds.

- **Cross-Validation Visualization:**  
  - **`plot_cv_boxplots(cv_metrics, output_dir='visualizations', title='Cross-Validation Metrics')`**  
    - **Purpose:** Generate box plots of cross-validation metrics, helping to compare performance variability across multiple models or different runs.

- **Model-Specific Visualizations:**  
  - **`plot_weight_bias_distribution(model_or_path, save_path=None)`**  
    - **Purpose:** Visualize the distribution of weights and biases across the layers of a model, which is useful for diagnosing training issues like vanishing gradients.  
  - **`plot_misclassified_examples(model_or_path, X_features, X_images, y, num_examples=5, save_path=None)`**  
    - **Purpose:** Display examples where the model misclassified the input, providing a qualitative view of model errors.



## Installation

### First option (Install Locally from GitLab)

1. Clone the repository:
    ```bash
    git clone https://gitlab2.informatik.uni-wuerzburg.de/hci/teaching/courses/machine-learning/student-submissions/ws24/Team-2/ml_framework_group_02.git
    cd ml_framework_group_02
    ```

2. Install the package using pip:
    ```bash
    import ml_framework_group_02
    ```

### Second option (Install from PyPI)

Once the package is published, anyone can install it directly from PyPI:

```bash
pip install ml_framework
```

