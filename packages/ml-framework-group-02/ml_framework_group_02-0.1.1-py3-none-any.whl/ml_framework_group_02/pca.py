import numpy as np

class PCA:
    def __init__(self, n_components):
        self.n_components = n_components
        self.mean = None
        self.components = None
        self.explained_variance = None
    
    def fit(self, X):
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean
        
        covariance_matrix = np.cov(X_centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        
        sorted_idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sorted_idx]
        eigenvectors = eigenvectors[:, sorted_idx]
        
        eigenvalues = eigenvalues[:self.n_components]
        eigenvectors = eigenvectors[:, :self.n_components]
        
        self.components = eigenvectors
        self.explained_variance = eigenvalues
    
    def transform(self, X):
        X_centered = X - self.mean
        
        return np.dot(X_centered, self.components)
    
    def fitTransform(self, X):
        self.fit(X)
        return self.transform(X)
    
    def inverseTransform(self, X_transformed):
        return np.dot(X_transformed, self.components.T) + self.mean
    
    def getExplainedVariance(self):
        return self.explained_variance
    
    def getExplainedVarianceRatio(self):
        return self.explained_variance / np.sum(self.explained_variance)