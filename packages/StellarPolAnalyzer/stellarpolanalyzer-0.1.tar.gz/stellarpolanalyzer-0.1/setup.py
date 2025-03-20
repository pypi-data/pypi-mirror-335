from setuptools import setup, find_packages

setup(
    name='StellarPolAnalyzer',
    version='0.1',
    description='Librería para análisis de imágenes polarimétricas y detección de parejas de estrellas',
    author='Oscar Mellizo Angulo',
    author_email='omellizo@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'astropy',
        'photutils',
        'scikit-learn',
    ],
)
