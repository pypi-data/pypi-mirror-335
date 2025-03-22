import numpy as np

class Random:
    def __init__(self, min = -0.01, max = 0.01):
        self.min = min
        self.max = max

    def __call__(self, in_cnt, out_cnt):
        return np.random.uniform(self.min, self.max, size=(out_cnt, in_cnt))
    
class Xavier:
    def __call__(self, in_cnt, out_cnt):
        limit = np.sqrt(6 / (in_cnt + out_cnt))
        return np.random.uniform(-limit, limit, size=(out_cnt, in_cnt))
    
class He:
    def __call__(self, in_cnt, out_cnt):
        limit = np.sqrt(2 / in_cnt)
        return np.random.uniform(-limit, limit, size=(out_cnt, in_cnt))