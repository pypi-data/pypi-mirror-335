
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="outly",  # Nombre en PyPI; verifica que esté disponible
    version="0.1.0",
    author="ESAI JOSUE HUAMAN MEZA",
    author_email="esai.huaman@gmail.com",
    description="Detección de outliers en Python con métodos estadísticos (Z-score e IQR).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/josuemzx/outly",  # Cambia a tu repo real
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "numpy>=1.17.0",
    ],
)
