from .utils import *

class MeanSquaredError:
    def __call__(self, predicted, actual):
        return mean_squared_error(predicted, actual)
    
    def derivative(self, predicted, actual):
        return mean_squared_error_derivative(predicted, actual)
    
class CrossEntropy:
    def __call__(self, predicted, actual):
        return cross_entropy(predicted, actual)
    
    def derivative(self, predicted, actual):
        return cross_entropy_derivative(predicted, actual)