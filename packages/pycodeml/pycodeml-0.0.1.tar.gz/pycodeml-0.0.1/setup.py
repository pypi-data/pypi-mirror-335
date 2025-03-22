from setuptools import setup, find_packages

setup(
    name="PyCodeml",
    version="0.0.1",
    description="Automatically Train multiple regression models and return the best one.",
    author="Nchiket",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
    ],
    python_requires=">=3.7",
)
