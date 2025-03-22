from setuptools import setup, find_packages

setup(
    name="pycodeml",
    version="0.0.3",
    description="Automatically Train multiple regression models and return the best one.",
    author="Nchiket",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
    ],
    python_requires=">=3.7",
)
