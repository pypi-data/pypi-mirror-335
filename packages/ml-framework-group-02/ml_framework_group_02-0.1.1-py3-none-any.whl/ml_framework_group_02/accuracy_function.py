import numpy as np
from .utils import *

class Accuracy:
    def __call__(self, predicted_label, label):
        correct = np.sum(predicted_label == label)
        return correct / len(label)
    
class Precision: # Macro-Precision
    def __call__(self, predicted_label, label):
        classes = np.unique(label)
        precisions = []
        for c in classes:
            tp = true_pos(predicted_label, label, c)
            fp = false_pos(predicted_label, label, c)
            precisions.append(precision(tp, fp))
        return np.mean(precisions) 

class Recall: # Macro-Recall
    def __call__(self, predicted_label, label):
        classes = np.unique(label)
        recalls = []
        for c in classes:
            tp = true_pos(predicted_label, label, c)
            fn = false_neg(predicted_label, label, c)
            recalls.append(recall(tp, fn))
        return np.mean(recalls) 

class F1Score: # Macro-F1
    def __call__(self, predicted_label, label):
        classes = np.unique(label)
        f1_scores = []
        for c in classes:
            tp = true_pos(predicted_label, label, c)
            fp = false_pos(predicted_label, label, c)
            fn = false_neg(predicted_label, label, c)

            prec = precision(tp, fp)
            rec = recall(tp, fn)
            f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
            f1_scores.append(f1)
        return np.mean(f1_scores) 