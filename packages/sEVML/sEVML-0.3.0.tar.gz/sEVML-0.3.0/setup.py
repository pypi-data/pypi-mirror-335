from setuptools import setup, find_packages

with open("README.md", "r") as f:
    descrition = f.read()

setup(
    name="sEVML",
    version="0.3.0",
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
    long_description=descrition,
    long_description_content_type="text/markdown",
)
