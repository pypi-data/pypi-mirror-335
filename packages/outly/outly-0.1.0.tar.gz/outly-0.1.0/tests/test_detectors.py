# tests/test_detectors.py
import numpy as np
from outly.detectors import ZScoreDetector, IQRDetector
from outly.utils import filter_outliers, replace_outliers

def test_zscore_detector():
    data = np.array([1, 2, 2, 3, 100])  # 100 es un outlier claro
    detector = ZScoreDetector(threshold=3.0).fit(data)
    outliers_mask = detector.predict(data)
    assert outliers_mask.sum() == 1  # Solo uno (100)

def test_iqr_detector():
    data = np.array([10, 12, 11, 10, 999])
    detector = IQRDetector(k=1.5).fit(data)
    outliers_mask = detector.predict(data)
    assert outliers_mask.sum() == 1  # Solo uno (999)

def test_utils():
    data = np.array([10, 12, 11, 10, 999])
    detector = IQRDetector(k=1.5).fit(data)
    mask = detector.predict(data)
    filtered = filter_outliers(data, mask)
    assert len(filtered) == 4  # 1 outlier filtrado

    replaced = replace_outliers(data, mask, replacement='median')
    # array sin outliers = [10, 12, 11, 10] => sorted [10, 10, 11, 12]
    # median = (10 + 11)/2 = 10.5
    assert replaced[-1] == 10.5
