import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
import math
from matplotlib.colors import PowerNorm
from IPython.display import display  
from .neural_network import*
import json

METRIC_NAMES = ["Accuracy", "Precision", "Recall", "F1 Score"]


def load_metrics(model_name, save_dir='saved_metrics'):
    metrics_file = os.path.join(save_dir, f"{model_name}_metrics.json")
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    print(f"Loaded metrics for {model_name} from: {metrics_file}")
    return metrics


def extract_accuracy_metrics(accuracy_history, metric_names=METRIC_NAMES):
    extracted = {m: [] for m in metric_names}
    for epoch_array in accuracy_history:
        epoch_values = epoch_array.tolist()
        for idx, metric in enumerate(metric_names):
            extracted[metric].append(epoch_values[idx])
    return extracted

def generate_model_metrics(model, X_test, y_test, model_name, save_dir='saved_metrics'):
    final_loss, final_accuracies, final_confusion_mat = model.test(X_test, y_test)
    validation_loss_history = model.get_val_loss_history()     # validation loss
    training_loss_history = model.get_train_loss_history()   # training loss
    raw_accuracy_history = model.get_accuracy_history()   
    training_accuracy_metrics = extract_accuracy_metrics(raw_accuracy_history, METRIC_NAMES)
    
    metrics = {
        "final_loss": final_loss,
        "final_accuracies": final_accuracies, 
        "confusion_matrix": final_confusion_mat,  
        "validation_loss_history": validation_loss_history,
        "training_loss_history": training_loss_history,
        "training_accuracy_metrics": training_accuracy_metrics,
        "training_accuracy": training_accuracy_metrics["Accuracy"],
        "training_precision": training_accuracy_metrics["Precision"],
        "training_recall": training_accuracy_metrics["Recall"],
        "training_f1": training_accuracy_metrics["F1 Score"],
        
    }
    
    os.makedirs(save_dir, exist_ok=True)
    metrics_file = os.path.join(save_dir, f"{model_name}_metrics.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else o)
    print(f"Saved metrics for {model_name} to: {metrics_file}")
    
    visualize_final_accuracies(final_accuracies)
    return metrics



def analyze_dataset_distribution(y_train, y_test):
    train_counts = np.bincount(y_train)
    test_counts = np.bincount(y_test)
    
    print("Training class distribution:", train_counts)
    print("Test class distribution:", test_counts)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].bar(np.arange(len(train_counts)), train_counts)
    axes[0].set_title("Training Class Distribution")
    axes[0].set_xlabel("Class")
    axes[0].set_ylabel("Frequency")
    
    axes[1].bar(np.arange(len(test_counts)), test_counts)
    axes[1].set_title("Test Class Distribution")
    axes[1].set_xlabel("Class")
    axes[1].set_ylabel("Frequency")
    
    plt.tight_layout()
    plt.show()
    
    return {
        "training_class_distribution": train_counts,
        "test_class_distribution": test_counts
    }


def visualize_final_accuracies(final_accuracies):
    fig, ax = plt.subplots(figsize=(8, 6))
    test_metric_names = METRIC_NAMES
    test_metric_values = final_accuracies
    ax.bar(test_metric_names, test_metric_values, color='skyblue')
    ax.set_title("Test Metrics", fontsize=16)
    ax.set_ylabel("Value", fontsize=14)
    plt.show()


def plot_metric_across_models(metric_key, models_metrics, model_names, 
                              title=None, ylabel=None, save_path=None, class_names=None):

    if metric_key.lower() in ["training_vs_validation_loss", "loss_history_comparison"]:
        title, ylabel = plot_loss_comparison(models_metrics, model_names, title, ylabel)
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight')
            print("Plot saved to:", save_path)
        plt.show()
        plt.close()
        return

    if metric_key.lower().startswith("confusion_matrix_scaled_"):
        # Extract scaling parameter from the metric key string
        try:
            scaling_str = metric_key.lower().split("confusion_matrix_scaled_")[1]
            scaling = float(scaling_str)
        except (IndexError, ValueError):
            print("Invalid scaling parameter provided in metric_key. Using default scaling=0.5.")
            scaling = 0.5

        # Determine class names if not provided
        if class_names is None:
            first_cm = models_metrics[0].get("confusion_matrix")
            if first_cm is not None:
                n = len(first_cm)
                class_names = [str(i) for i in range(n)]
            else:
                class_names = []
        
        # Loop through each model's metrics and plot using the scaled function
        for metrics, name in zip(models_metrics, model_names):
            conf_mat = metrics.get("confusion_matrix")
            if conf_mat is None:
                print(f"No confusion matrix found for model {name}")
                continue
            model_save_path = None
            if save_path:
                base, ext = os.path.splitext(save_path)
                model_save_path = f"{base}_{name}{ext}"
            print(f"Plotting scaled confusion matrix (scaling={scaling}) for model {name}")
            scaled_confusion_matrix(np.array(conf_mat), class_names, scaling=scaling, save_path=model_save_path)
        return

    elif metric_key.lower() == "confusion_matrix":
        if class_names is None:
            first_cm = models_metrics[0].get("confusion_matrix")
            if first_cm is not None:
                n = len(first_cm)
                class_names = [str(i) for i in range(n)]
            else:
                class_names = []
        for metrics, name in zip(models_metrics, model_names):
            conf_mat = metrics.get("confusion_matrix")
            if conf_mat is None:
                print(f"No confusion matrix found for model {name}")
                continue
            model_save_path = None
            if save_path:
                base, ext = os.path.splitext(save_path)
                model_save_path = f"{base}_{name}{ext}"
            print(f"Plotting confusion matrix for model {name}")
            plot_confusion_matrix(np.array(conf_mat), class_names, save_path=model_save_path)
        return


    if metric_key.lower() == "training_accuracy_metrics":
        plot_training_accuracy_metrics(models_metrics, model_names)
        if title is None:
            title = "Training Accuracy Metrics Comparison"
        if ylabel is None:
            ylabel = "Metric Value"
        plt.title(title, fontsize=16)
        plt.xlabel("Epoch", fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight')
            print("Plot saved to:", save_path)
        plt.show()
        plt.close()
        return

    # Default branch for other metrics
    if title is None:
        title = f"{metric_key.replace('_', ' ').title()} Comparison"
    ylabel = get_metric_name(metric_key, ylabel)
    
    if save_path is None:
        safe_metric_key = metric_key.lower().replace(" ", "_")
        save_path = f"combined_{safe_metric_key}.png"
    
    plot_metric_over_epochs(metric_key, models_metrics, model_names, title, ylabel)
    
    if save_path:
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight')
        print("Plot saved to:", save_path)
    
    plt.show()
    plt.close()

def plot_loss_comparison(models_metrics, model_names, title, ylabel):
    plt.figure(figsize=(10, 6))
    for metrics, name in zip(models_metrics, model_names):
        training_loss = metrics.get("training_loss_history", [])
        validation_loss = metrics.get("validation_loss_history", [])
        if not training_loss or not validation_loss:
            print(f"Missing loss history for model {name}")
            continue
        epochs = list(range(1, len(training_loss) + 1))
        plt.plot(epochs, training_loss, label=f"{name} - Training Loss", linewidth=2)
        plt.plot(epochs, validation_loss, label=f"{name} - Validation Loss", linewidth=2)
    if title is None:
        title = "Training vs Validation Loss"
    if ylabel is None:
        ylabel = "Loss"
    plt.title(title, fontsize=16)
    plt.xlabel("Epoch", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    return title,ylabel

def plot_training_accuracy_metrics(models_metrics, model_names):
    plt.figure(figsize=(10, 6))
    line_styles = {
            "Accuracy": "solid",
            "Precision": "dashed",
            "Recall": "dotted",
            "F1 Score": "dashdot"
        }
    cmap = plt.get_cmap("tab10")
    for i, (metrics, name) in enumerate(zip(models_metrics, model_names)):
        training_acc_metrics = metrics.get("training_accuracy_metrics")
        if not training_acc_metrics:
            print(f"No training_accuracy_metrics found for model {name}")
            continue
        epochs = range(1, len(training_acc_metrics.get("Accuracy", [])) + 1)
        for metric, style in line_styles.items():
            metric_values = training_acc_metrics.get(metric, [])
            if not metric_values:
                print(f"No data for {metric} in model {name}")
                continue
            plt.plot(epochs, metric_values, label=f"{name} - {metric}", 
                         linestyle=style, color=cmap(i), linewidth=2)



def plot_metric_over_epochs(metric_key, models_metrics, model_names, title, ylabel):
    plt.figure(figsize=(10, 6))
    for metrics, name in zip(models_metrics, model_names):
        values = metrics.get(metric_key, [])
        epochs = list(range(1, len(values) + 1))
        plt.plot(epochs, values, label=name, linewidth=2)
    plt.title(title, fontsize=16)
    plt.xlabel("Epoch", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()


def get_metric_name(metric_key, ylabel):
    if ylabel is None:
        key_lower = metric_key.lower()
        if "accuracy" in key_lower:
            ylabel = "Accuracy"
        elif "precision" in key_lower:
            ylabel = "Precision"
        elif "recall" in key_lower:
            ylabel = "Recall"
        elif "f1" in key_lower:
            ylabel = "F1 Score"
        elif "loss" in key_lower:
            ylabel = "Loss"
        else:
            ylabel = "Value"
    return ylabel



def plot_smoothed_loss_history(loss_history, window_size=5, output_dir='visualizations', title='Smoothed Training Loss'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    loss_history = np.array(loss_history)
    if len(loss_history) < window_size:
        smoothed_loss = loss_history
        epochs = np.arange(1, len(loss_history) + 1)
    else:
        smoothed_loss = np.convolve(loss_history, np.ones(window_size) / window_size, mode='valid')
        epochs = np.arange(window_size, len(loss_history) + 1)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(epochs, smoothed_loss, marker='o', linestyle='-', color='red')
    ax.set_title(title, fontsize=12, pad=15)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.grid(True)

    smoothed_loss_path = os.path.join(output_dir, "smoothed_loss_plot.png")

    if output_dir:
        plt.savefig(smoothed_loss_path, bbox_inches='tight')
        print("Smoothed loss plot saved to:", smoothed_loss_path)

        display(fig)  
        plt.close(fig)  
    else:
        plt.show()

def plot_train_val_loss_history(train_loss_history, val_loss_history, output_dir='visualizations'):
    epochs = np.arange(1, len(train_loss_history) + 1)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(epochs, train_loss_history, marker='o', linestyle='-', label='Training Loss')
    ax.plot(epochs, val_loss_history, marker='o', linestyle='-', label='Validation Loss')
    ax.set_title("Training vs Validation Loss", fontsize=12, pad=15)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.grid(True)
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        loss_plot_path = os.path.join(output_dir, "train_val_loss_history.png")
        plt.savefig(loss_plot_path, bbox_inches='tight')
        print("Train vs Validation loss plot saved to:", loss_plot_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show() 


# ----------------------
# Confusion Matrix Visualization
# ----------------------

def plot_confusion_matrix(confusion_matrix, class_names, save_path=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    cax = ax.imshow(confusion_matrix, cmap="Blues", interpolation="nearest")
    fig.colorbar(cax)
    ax.set_xlabel("Predicted Labels")
    ax.set_ylabel("True Labels")
    ax.set_title("Confusion Matrix", fontsize=12, pad=10)
    
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(class_names, fontsize=10)
    
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            ax.text(j, i, str(confusion_matrix[i, j]),
                    ha="center", va="center", color="black", fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(save_path, bbox_inches="tight")
        print("Confusion matrix plot saved to:", save_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()

def scaled_confusion_matrix(confusion_matrix, class_names, scaling=0.5, save_path=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # power-law normalization
    norm = PowerNorm(gamma=scaling)
    cax = ax.imshow(confusion_matrix, cmap="Blues", norm=norm, interpolation="nearest")
    fig.colorbar(cax)
    
    ax.set_xlabel("Predicted Labels")
    ax.set_ylabel("True Labels")
    ax.set_title("Scaled Confusion Matrix", fontsize=12, pad=10)
    
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(class_names, fontsize=10)
    
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            ax.text(j, i, str(confusion_matrix[i, j]),
                    ha="center", va="center", color="black", fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(save_path, bbox_inches="tight")
        print("Scaled confusion matrix plot saved to:", save_path)
        plt.show()
        plt.close(fig)
    else:
        plt.show()


def plot_test_metrics(final_accuracies, output_dir=None, metrics_bar_path='test_metrics_bar_chart.png'):

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(METRIC_NAMES, final_accuracies, color='skyblue')
    ax.set_title("Final Test Metrics", fontsize=16)
    ax.set_ylabel("Metric Value", fontsize=14)
    ax.set_ylim(0, 1)  # assuming metric values are in the range [0, 1]
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save or display the figure based on the provided output_dir
    if output_dir:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, metrics_bar_path)
        plt.savefig(full_path, bbox_inches='tight')
        print("Test metrics bar chart saved to:", full_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()


# ----------------------
# ROC & Precision-Recall Visualizations
# ----------------------

def expit(x):
    return 1 / (1 + np.exp(-x))

def compute_roc_curve(y_true, y_score, num_thresholds=100):
    thresholds = np.linspace(0, 1, num_thresholds)
    tpr = []
    fpr = []
    P = np.sum(y_true)      
    N = len(y_true) - P     
    for thresh in thresholds:
        # Predicted as positive if score >= threshold
        pred = (y_score >= thresh).astype(int)
        TP = np.sum((pred == 1) & (y_true == 1))
        FP = np.sum((pred == 1) & (y_true == 0))
        tpr.append(TP / P if P > 0 else 0)
        fpr.append(FP / N if N > 0 else 0)
    return np.array(fpr), np.array(tpr)

def plot_roc_curves(y_score, y_true, classes, output_dir='visualizations'):
    if np.min(y_score) < 0 or np.max(y_score) > 1:
        y_score = expit(y_score)
    
    if y_true.ndim == 1:
        y_true = np.eye(len(classes))[y_true]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, class_name in enumerate(classes):
        fpr, tpr = compute_roc_curve(y_true[:, i], y_score[:, i])
        # Calculate AUC using integration
        roc_auc = np.trapz(tpr, fpr)
        ax.plot(fpr, tpr, lw=2, label=f'{class_name} (AUC = {roc_auc:.2f})')
    
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver Operating Characteristic (ROC) Curves', fontsize=12, pad=15)
    ax.legend(loc="lower right")
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        roc_path = os.path.join(output_dir, "roc_curves.png")
        plt.savefig(roc_path, bbox_inches='tight')
        print("ROC curves saved to:", roc_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()



def compute_precision_recall_curve(y_true, y_score, num_thresholds=100):
    thresholds = np.linspace(0, 1, num_thresholds)
    precision_list = []
    recall_list = []
    P = np.sum(y_true)  
    for thresh in thresholds:
        pred = (y_score >= thresh).astype(int)
        TP = np.sum((pred == 1) & (y_true == 1))
        FP = np.sum((pred == 1) & (y_true == 0))
        FN = np.sum((pred == 0) & (y_true == 1))
        rec = TP / (TP + FN) if (TP + FN) > 0 else 0
        prec = TP / (TP + FP) if (TP + FP) > 0 else 1
        recall_list.append(rec)
        precision_list.append(prec)
    return np.array(recall_list), np.array(precision_list)


def expit(x):
    return 1 / (1 + np.exp(-x))

def plot_precision_recall_curves(y_true, y_score, classes, output_dir='visualizations'):
    if np.min(y_score) < 0 or np.max(y_score) > 1:
        y_score = expit(y_score)
    if y_true.ndim == 1:
        y_true = np.eye(len(classes))[y_true]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, class_name in enumerate(classes):
        recall, precision = compute_precision_recall_curve(y_true[:, i], y_score[:, i])
        # Compute average precision as the area under the precision-recall curve using the trapezoidal rule
        avg_precision = np.trapz(precision, recall)
        ax.plot(recall, precision, lw=2, label=f'{class_name} (AP = {avg_precision:.2f})')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title('Precision-Recall Curves', fontsize=12, pad=15)
    ax.legend(loc="lower left")
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        pr_path = os.path.join(output_dir, "precision_recall_curves.png")
        plt.savefig(pr_path, bbox_inches='tight')
        print("Precision-Recall curves saved to:", pr_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()
        
# ----------------------
# Cross-Validation Box Plot Visualization
# ----------------------
def plot_cv_boxplots(cv_metrics, output_dir='visualizations', title='Cross-Validation Metrics'):
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    metric_names = list(cv_metrics.keys())
    data = [cv_metrics[m] for m in metric_names]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data, labels=metric_names)
    ax.set_title(title)
    ax.set_ylabel("Score")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    if output_dir:
        cv_plot_path = os.path.join(output_dir, "cv_boxplots.png")
        plt.savefig(cv_plot_path, bbox_inches='tight')
        print("Cross-validation box plots saved to:", cv_plot_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()

# ----------------------
# Weight & Bias Distribution Visualization
# ----------------------

# for vanishing gradients...

def plot_weight_bias_distribution(model_or_path, save_path=None):
    if isinstance(model_or_path, str):
        model = Classifier.load(model_or_path)
        if model is None:
            print("Failed to load model from:", model_or_path)
            return
    else:
        model = model_or_path

    layers = model.layers
    n_layers = len(layers)
    
    fig, axes = plt.subplots(n_layers, 2, figsize=(12, n_layers * 4))

    if n_layers == 1:
        axes = np.array([axes])

    for idx, layer in enumerate(layers):
        weights = layer.weights.flatten()
        biases = layer.biases.flatten()

        ax_w = axes[idx, 0]
        ax_w.hist(weights, bins=30, color='skyblue', edgecolor='black')
        ax_w.set_title(f"Layer {idx+1} Weights Distribution", fontsize=12, pad=15)
        ax_w.set_xlabel("Weight values")
        ax_w.set_ylabel("Frequency")
        ax_w.grid(True, linestyle='--', alpha=0.6)

        ax_b = axes[idx, 1]
        ax_b.hist(biases, bins=30, color='salmon', edgecolor='black')
        ax_b.set_title(f"Layer {idx+1} Biases Distribution", fontsize=12, pad=15)
        ax_b.set_xlabel("Bias values")
        ax_b.set_ylabel("Frequency")
        ax_b.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  

    if save_path:
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(save_path, bbox_inches='tight')
        print("Weight and bias distribution plot saved to:", save_path)
        display(fig)
        plt.close(fig)
    else:
        plt.show()



def plot_misclassified_examples(model_or_path, X_features, X_images, y, num_examples=5, save_path=None):
    if isinstance(model_or_path, str):
        model = Classifier.load(model_or_path)
        if model is None:
            print("Failed to load model from:", model_or_path)
            return
    else:
        model = model_or_path

    predicted = model.predict_label(X_features)
    y = np.array(y)
    mis_idx = np.where(predicted != y)[0]
    if len(mis_idx) == 0:
        print("No misclassified examples found.")
        return
    num_to_plot = min(num_examples, len(mis_idx))

    ncols = num_to_plot
    nrows = 1
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 5 * nrows)) 

    for i, idx in enumerate(mis_idx[:num_to_plot]):
        ax = axes[i] if num_to_plot > 1 else axes  
        sample = X_images[idx]
        
        if sample.ndim == 2:
            ax.imshow(sample, cmap='gray')
        elif sample.ndim == 1:
            side = int(math.sqrt(sample.size))
            if side * side == sample.size:
                sample_reshaped = sample.reshape((side, side))
                ax.imshow(sample_reshaped, cmap='gray')
            else:
                ax.plot(sample, marker='o')
                ax.set_xlabel("Feature Index")
                ax.set_ylabel("Value")
        else:
            ax.imshow(sample)
        
        ax.set_title(f"True: {y[idx]}\nPred: {predicted[idx]}", fontsize=12, pad=15)
        ax.axis('off')
    plt.subplots_adjust(top=0.85)

    if save_path:
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(save_path, bbox_inches='tight')
        print("Misclassified examples plot saved to:", save_path)
        display(fig)  
        plt.close(fig)  
    else:
        plt.show()  

