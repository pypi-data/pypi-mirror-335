import numpy as np

def sigmoid(x):
    val = 1 / (1 + np.exp(-x))
    return 1 / (1 + np.exp(-x))
        
def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

def tanh(x):
    return np.tanh(x)

def tanh_derivative(x):
    return 1 - tanh(x)**2

def leaky_relu(x, alpha):
    return np.where(x > 0, x, alpha * x)

def leaky_relu_derivative(x, alpha):
    return np.where(x > 0, 1, alpha)

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

def softmax_derivative(x):
    s = softmax(x)
    batch_size, num_classes = s.shape
    jacobi_matrices = np.zeros((batch_size, num_classes, num_classes))
    
    for b in range(batch_size):
        s_b = s[b].reshape(-1, 1)
        jacobi_matrices[b] = np.diagflat(s_b) - np.dot(s_b, s_b.T)
    
    return jacobi_matrices

def mean_squared_error(predicted, actual):
    return 1 / 2 * np.mean(np.square(predicted - actual))

def mean_squared_error_derivative(predicted, actual):
    return (predicted - actual) / len(actual)

def cross_entropy(predicted, actual):
    epsilon = 1e-12
    predicted = np.clip(predicted, epsilon, 1 - epsilon)
    return -np.mean(np.sum(actual * np.log(predicted), axis=1))

def cross_entropy_derivative(predicted, actual):
    return predicted - actual

def argmax(x):
    return np.argmax(x, axis = 1)

def one_hot(x, class_count):
    return np.eye(class_count)[x]

def true_pos(predicted, actual, class_label):
    return np.sum((predicted == class_label) & (actual == class_label))

def false_pos(predicted, actual, class_label):
    return np.sum((predicted == class_label) & (actual != class_label))

def false_neg(predicted, actual, class_label):
    return np.sum((predicted != class_label) & (actual == class_label))

def precision(true_pos, false_pos):
    return true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0

def recall(true_pos, false_neg):
    return true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0