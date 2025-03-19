from setuptools import setup, find_packages

setup(
    name="scanpy_clustering",
    version="0.1.0",
    description="Modular clustering extension for scanpy",
    author="Daniel Sutton",
    packages=find_packages(),
    install_requires=[
        "scanpy>=1.9.0",
        "numpy>=1.20.0",
        "anndata>=0.8.0",
        "scipy>=1.6.0",
    ],
    python_requires=">=3.8",
) 