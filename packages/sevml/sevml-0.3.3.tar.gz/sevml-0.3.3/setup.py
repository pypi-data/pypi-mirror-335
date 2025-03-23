from setuptools import setup, find_packages

with open("README.md", "r") as f:
    descrition = f.read()

setup(
    name="sevml",
    version="0.3.3",
    description="Machine learning tools for biological analysis",
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
            "sevml = sevml.main:main"
        ]
    },
    long_description=descrition,
    long_description_content_type="text/markdown",
)
