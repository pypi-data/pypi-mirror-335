import numpy as np
import pickle
from .bias_init_function import *
from .utils import *
from .activation_function import *
from .optimizer_function import *
from .loss_function import *
from .accuracy_function import *
from .nn_layer import *
from .weight_init_function import *

class Classifier:
    def __init__(self, stack, optimizer_function = Adam(), loss_function = CrossEntropy(), accuracy_functions=[Accuracy(), Precision(), Recall(), F1Score()]): 
        self.stack = stack
        self.layers = [s for s in stack if isinstance(s, Layer)] # references from objects in stack
        self.layer_cnt = len(self.layers)

        self.class_cnt = self.layers[-1].weights.shape[0]

        self.optimizer_function = optimizer_function

        self.loss_function = loss_function
        self.accuracy_functions = accuracy_functions

        self.val_loss_history = []
        self.train_loss_history = []
        self.accuracy_history = []

    def forward(self, input):
        output = np.full(self.layer_cnt + 1, None)
        unactivated_output = np.full(self.layer_cnt + 1, None)
        output[0] = input
        unactivated_output[0] = input

        i = 0
        for s in self.stack:
            if isinstance(s, Layer):
                unactivated = output[i] @ s.weights.T + s.biases
                i += 1
                unactivated_output[i] = unactivated
                output[i] = unactivated
            else: # activation function
                output[i] = s(output[i])

        return output, unactivated_output
    
    def backward(self, output, unactivated_output, actual):
        delta = np.full(self.layer_cnt, None)
        gradients_weights = np.full(self.layer_cnt, None)
        gradients_biases = np.full(self.layer_cnt, None)

        delta[-1] = self.loss_function.derivative(output[-1], actual)

        i = self.layer_cnt - 1
        for s in reversed(self.stack):
            if isinstance(s, Layer):
                gradients_weights[i] = delta[i].T @ output[i]
                gradients_biases[i] = np.sum(delta[i], axis=0)
                i -= 1
                if i >= 0:
                    delta[i] = delta[i+1] @ self.layers[i+1].weights
            else: # activation function
                derivative, is_jacobean = s.derivative(unactivated_output[i+1])
                if is_jacobean:
                    delta[i] = np.einsum('bij,bj->bi', derivative, delta[i]) # special batchwise multiplication
                else:
                    delta[i] = derivative * delta[i]

        return gradients_weights, gradients_biases
        


    def train(self, epochs, input, labels, folds=5, stop_patience=10, log_epochs=10, history_epochs=10):
        self.val_loss_history = []
        self.train_loss_history = []
        self.accuracy_history = []
        
        fold_size = len(input) // folds

        for fold in range(folds):
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold != folds - 1 else len(input)

            val_input = input[val_start:val_end]
            val_labels = labels[val_start:val_end]
            val_actual = one_hot(val_labels, self.class_cnt)
            train_input = np.concatenate([input[:val_start], input[val_end:]], axis=0)
            train_labels = np.concatenate([labels[:val_start], labels[val_end:]], axis=0)
            train_actual = one_hot(train_labels, self.class_cnt)

            no_improvement_epochs = 0
            min_loss = float('inf')
            best_layers = self.layers

            for epoch in range(epochs):
                output, unactivated_output = self.forward(train_input)
                gradients_weights, gradients_biases = self.backward(output, unactivated_output, train_actual)
                self.optimizer_function(self.layers, gradients_weights, gradients_biases)

                val_loss = self.loss_function(self.predict(val_input), val_actual)
                train_loss = self.loss_function(self.predict(train_input), train_actual)

                if min_loss < val_loss:
                    no_improvement_epochs += 1
                    if no_improvement_epochs >= stop_patience:
                        print(f"Stopped at: Fold: {fold + 1}; Epoch {epoch + 1}:")
                        self.layers = best_layers
                        break
                else:
                    min_loss = val_loss
                    no_improvement_epochs = 0
                    best_layers = self.layers.copy()

                log = log_epochs > 0 and (epoch + 1) % log_epochs == 0
                history = history_epochs > 0 and (epoch + 1) % history_epochs == 0

                if log or history:
                    accuracies = np.full(len(self.accuracy_functions), None)
                    for i, accuracy_function in enumerate(self.accuracy_functions):
                        accuracies[i] = accuracy_function(self.predict_label(val_input), val_labels)
                    if log:
                        print(f"Fold: {fold + 1}; Epoch {epoch + 1}:")
                        print(f"Validation Loss({self.loss_function.__class__.__name__}): {val_loss}")
                        print(f"Training Loss({self.loss_function.__class__.__name__}): {train_loss}")
                        for i, accuracy_function in enumerate(self.accuracy_functions):
                            print(f"Accuracy({accuracy_function.__class__.__name__}): {accuracies[i]}")
                    if history:
                        self.val_loss_history.append(val_loss)
                        self.train_loss_history.append(train_loss)
                        self.accuracy_history.append(accuracies)
    
    def predict(self, inputs):
        out, _ = self.forward(inputs)
        return out[-1]
    
    def predict_label(self, inputs):
        out, _ = self.forward(inputs)
        return argmax(out[-1])

    def get_accuracy_history(self):
        return self.accuracy_history
    
    def get_val_loss_history(self):
        return self.val_loss_history
    
    def get_train_loss_history(self):
        return self.train_loss_history

    def test(self, input, labels):
        predicted = self.predict(input)
        predicted_labels = argmax(predicted)
        actual = one_hot(labels, self.class_cnt)
        
        loss = self.loss_function(predicted, actual)

        accuracies = np.full(len(self.accuracy_functions), None)
        for i, accuracy_function in enumerate(self.accuracy_functions):
            accuracies[i] = accuracy_function(predicted_labels, labels)
        
        confusion_mat = np.zeros((self.class_cnt, self.class_cnt), dtype=int)
        for pred_label, label in zip(predicted_labels, labels):
            confusion_mat[pred_label, label] += 1
        
        return loss, accuracies, confusion_mat

    def save(self, path):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    def run_cross_validation(self, X_train, y_train, epochs=50, folds=5, stop_patience=10, log_epochs=10, history_epochs=10):
        cv_metrics = {
            'Accuracy': [],
            'Precision': [],
            'Recall': [],
            'F1Score': []
        }
        
        fold_size = len(X_train) // folds
        for fold in range(folds):
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold != folds - 1 else len(X_train)
            
            val_input = X_train[val_start:val_end]
            val_labels = y_train[val_start:val_end]
            
            train_input = np.concatenate([X_train[:val_start], X_train[val_end:]], axis=0)
            train_labels = np.concatenate([y_train[:val_start], y_train[val_end:]], axis=0)
            
            self.train(
                epochs=epochs,
                input=train_input,
                labels=train_labels,
                folds=1,  
                stop_patience=stop_patience,
                log_epochs=log_epochs,
                history_epochs=history_epochs
            )
            

            loss, accuracies, confusion = self.test(val_input, val_labels)
            cv_metrics['Accuracy'].append(accuracies[0])
            cv_metrics['Precision'].append(accuracies[1])
            cv_metrics['Recall'].append(accuracies[2])
            cv_metrics['F1Score'].append(accuracies[3])
            
            print(f"Fold {fold+1} results: Loss = {loss}, Accuracy = {accuracies[0]}")
        
        return cv_metrics

    @staticmethod
    def load(path):
        try:
            with open(path, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            print(f"File {path} was not found.")
            return None