from setuptools import setup, find_packages

setup(
    name="auto_trading",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-binance",
        "pandas",
        "numpy"
    ],
)
