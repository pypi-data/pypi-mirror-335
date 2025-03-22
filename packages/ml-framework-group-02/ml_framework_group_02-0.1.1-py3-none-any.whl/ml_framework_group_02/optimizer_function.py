import numpy as np

class GradientDescent:
    def __init__(self, learning_rate = 0.01):
        self.learning_rate = learning_rate

    def __call__(self, layers, gradients_weights, gradients_biases):
        for i in range(len(layers)):
            layers[i].weights -= gradients_weights[i] * self.learning_rate
            layers[i].biases -= gradients_biases[i] * self.learning_rate
    
class MomentumGradientDescent:
    def __init__(self, learning_rate = 0.01, beta = 0.9):
        self.learning_rate = learning_rate
        self.beta = beta

        self.velocity_weights = None
        self.velocity_biases = None

    def __call__(self, layers, gradients_weights, gradients_biases):
        if self.velocity_weights is None:
            self.velocity_weights = [np.zeros_like(l.weights) for l in layers]
            self.velocity_biases = [np.zeros_like(l.biases) for l in layers]

        for i in range(len(layers)):
            self.velocity_weights[i] = self.beta * self.velocity_weights[i] + (1 - self.beta) * gradients_weights[i]
            layers[i].weights -= self.learning_rate * self.velocity_weights[i]
            
            self.velocity_biases[i] = self.beta * self.velocity_biases[i] + (1 - self.beta) * gradients_biases[i]
            layers[i].biases -= self.learning_rate * self.velocity_biases[i]
    
class Adam:
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.learning_rate = learning_rate
        self.beta1 = beta1 
        self.beta2 = beta2
        self.epsilon = epsilon
        
        self.m_weights = None
        self.v_weights = None
        self.m_biases = None
        self.v_biases = None
        self.t = 0

    def __call__(self, layers, gradients_weights, gradients_biases):
        self.t += 1
        
        if self.m_weights is None:
            self.m_weights = [np.zeros_like(l.weights) for l in layers]
            self.v_weights = [np.zeros_like(l.weights) for l in layers]
            self.m_biases = [np.zeros_like(l.biases) for l in layers]
            self.v_biases = [np.zeros_like(l.biases) for l in layers]

        for i in range(len(layers)):
            self.m_weights[i] = self.beta1 * self.m_weights[i] + (1 - self.beta1) * gradients_weights[i]
            self.v_weights[i] = self.beta2 * self.v_weights[i] + (1 - self.beta2) * (gradients_weights[i] ** 2)

            self.m_biases[i] = self.beta1 * self.m_biases[i] + (1 - self.beta1) * gradients_biases[i]
            self.v_biases[i] = self.beta2 * self.v_biases[i] + (1 - self.beta2) * (gradients_biases[i] ** 2)

            m_hat_weights = self.m_weights[i] / (1 - self.beta1 ** self.t)
            v_hat_weights = self.v_weights[i] / (1 - self.beta2 ** self.t)
            m_hat_biases = self.m_biases[i] / (1 - self.beta1 ** self.t)
            v_hat_biases = self.v_biases[i] / (1 - self.beta2 ** self.t)

            layers[i].weights -= self.learning_rate * m_hat_weights / (np.sqrt(v_hat_weights) + self.epsilon)
            layers[i].biases -= self.learning_rate * m_hat_biases / (np.sqrt(v_hat_biases) + self.epsilon)