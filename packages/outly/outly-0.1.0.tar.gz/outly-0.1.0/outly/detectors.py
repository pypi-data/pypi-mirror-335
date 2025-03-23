# outly/detectors.py
import numpy as np

class ZScoreDetector:
    """
    Detecta outliers basados en Z-score.
    Marca como outlier aquel valor cuyo Z-score
    exceda un umbral (por defecto 3.0).
    """

    def __init__(self, threshold=3.0):
        """
        :param threshold: Valor de corte del Z-score.
        """
        self.threshold = threshold

    def fit(self, data):
        """
        Calcula la media y desviación estándar para uso interno.

        :param data: Lista o numpy array de valores.
        """
        data = np.array(data, dtype=float)
        self.mean_ = np.mean(data)
        self.std_ = np.std(data)
        return self

    def predict(self, data):
        """
        Retorna un array de booleans indicando si el punto
        es outlier (True) o no (False).
        """
        data = np.array(data, dtype=float)
        z_scores = (data - self.mean_) / (self.std_ + 1e-9)
        return np.abs(z_scores) > self.threshold

    def fit_predict(self, data):
        """
        Combina fit y predict para conveniencia.
        """
        self.fit(data)
        return self.predict(data)


class IQRDetector:
    """
    Detecta outliers basados en rango intercuartílico (IQR).
    Marca como outlier aquel valor < Q1 - k*IQR o > Q3 + k*IQR.
    """

    def __init__(self, k=1.5):
        """
        :param k: Factor multiplicador del IQR.
        """
        self.k = k

    def fit(self, data):
        """
        Calcula Q1, Q3 e IQR para uso interno.

        :param data: Lista o numpy array de valores.
        """
        data = np.array(data, dtype=float)
        self.q1_ = np.percentile(data, 25)
        self.q3_ = np.percentile(data, 75)
        self.iqr_ = self.q3_ - self.q1_
        return self

    def predict(self, data):
        """
        Retorna un array de booleans indicando si el punto
        es outlier (True) o no (False).
        """
        data = np.array(data, dtype=float)
        lower_bound = self.q1_ - self.k * self.iqr_
        upper_bound = self.q3_ + self.k * self.iqr_
        return (data < lower_bound) | (data > upper_bound)

    def fit_predict(self, data):
        """
        Combina fit y predict para conveniencia.
        """
        self.fit(data)
        return self.predict(data)
