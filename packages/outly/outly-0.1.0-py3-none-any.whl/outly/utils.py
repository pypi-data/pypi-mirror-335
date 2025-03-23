# outly/utils.py
import numpy as np

def filter_outliers(data, outliers_mask):
    """
    Retorna los valores no outliers de 'data', según un array
    de booleans (True = outlier).
    """
    data = np.array(data)
    return data[~outliers_mask]


def replace_outliers(data, outliers_mask, replacement='median'):
    """
    Reemplaza los valores marcados como outliers en 'data'
    por 'replacement' (puede ser 'median', 'mean' o un valor numérico).
    """
    data = np.array(data, dtype=float)
    non_outliers = data[~outliers_mask]

    if replacement == 'median':
        rep_value = np.median(non_outliers)
    elif replacement == 'mean':
        rep_value = np.mean(non_outliers)
    else:
        rep_value = replacement  # asume que es un número

    data[outliers_mask] = rep_value
    return data
