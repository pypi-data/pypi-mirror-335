# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="geoxgboost",
    version="1.0.9",
    description="Geographically Weighted XGBoost",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://geoxgboost.readthedocs.io/",
    author="George Grekousis",
    author_email="geograik@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.9",
    packages=find_packages(include=['geoxgboost']),
    include_package_data=True,
    install_requires=[
        'pandas >= 2.1.4', 'numpy >=1.26.4', 'scikit-learn >= 1.4.2',
         'scipy >= 1.12.0', 'xgboost >= 2.0', 'openpyxl >= 3.0.9']
)
