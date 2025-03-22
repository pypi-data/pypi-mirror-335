from setuptools import setup, find_packages

setup(
    name="sEVML",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy<2",
        "matplotlib",
        "shap",
        "xgboost",
        "scikit-learn"
    ],
    entry_points={
        "console_scripts": [
            "sevml = sEVML.main:main"
        ]
    },
)
