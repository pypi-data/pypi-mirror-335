from setuptools import setup, find_packages

setup(
    name="vol_mom_pkg",
    version="0.1.9",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pandas_datareader',
        'alpaca-trade-api',
        'numpy',
        'yfinance',
        'python-dotenv',
        'setuptools',
    ],
    description='Volatility and momentum strategy, trades executed with Alpaca',
    author='Cassel Robson',
    author_email='robs7000@mylaurier.ca',
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
)