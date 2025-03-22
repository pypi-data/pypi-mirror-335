from .utils import *

class Sigmoid:
    def __call__(self, x):
        return sigmoid(x)
    
    def derivative(self, x):
        return sigmoid_derivative(x), False
    
class Tanh:
    def __call__(self, x):
        return tanh(x)
    
    def derivative(self, x):
        return tanh_derivative(x), False
    
class LeakyReLU:
    def __init__(self, alpha=0.01):
        self.alpha = alpha

    def __call__(self, x):
        return leaky_relu(x, self.alpha)
    
    def derivative(self, x):
        return leaky_relu_derivative(x, self.alpha), False
    
class Softmax:
    def __call__(self, x):
        return softmax(x)
    
    def derivative(self, x):
        return softmax_derivative(x), True
