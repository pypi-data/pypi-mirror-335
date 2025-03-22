import numpy as np

class Constant:
    def __init__(self, val = 0.01):
        self.val = val

    def __call__(self, out_cnt):
        return np.full(out_cnt, self.val)
    
class Random:
    def __init__(self, min = -0.01, max = 0.01):
        self.min = min
        self.max = max

    def __call__(self, out_cnt):
        return np.random.uniform(self.min, self.max, size=(out_cnt))