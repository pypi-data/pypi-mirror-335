import numpy as np
from .weight_init_function import *
from .bias_init_function import *

class Layer:
    def __init__(self, in_cnt, out_cnt, weight_init_function = He(), bias_init_function = Constant()):
        self.weights = weight_init_function(in_cnt, out_cnt)
        self.biases = bias_init_function(out_cnt)

    def in_size(self):
        return self.weights.shape[1]

    def out_size(self):
        return self.weights.shape[0]