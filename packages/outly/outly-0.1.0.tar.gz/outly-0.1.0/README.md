# Outly

**Outly** es una librería ligera para la **detección rápida de valores atípicos (outliers)** en Python usando métodos estadísticos sencillos (Z-score e IQR). El objetivo es ofrecer una solución minimalista para filtrar o reemplazar outliers en data sets sin instalar herramientas pesadas.

## Características principales

- **ZScoreDetector**: Marca como outliers los valores con un Z-score mayor a un umbral (p. ej., 3.0).
- **IQRDetector**: Utiliza el rango intercuartílico (IQR); marca outliers fuera de [Q1 - k*IQR, Q3 + k*IQR].
- **Funciones de utilidad**:
  - `filter_outliers()`: Filtra y devuelve solo los valores no atípicos.
  - `replace_outliers()`: Permite reemplazar outliers por mediana, media o un valor fijo.

## Instalación

Instala Outly desde PyPI con:

```bash
pip install outly
