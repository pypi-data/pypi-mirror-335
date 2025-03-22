from setuptools import setup, find_packages

setup(
    name="pycodeml",
    version="0.0.9",
    description="Automatically train multiple regression models and return the best one.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nachiket Shinde",
    author_email="nachiketshinde2004@gmail.com",  # Replace with your email
    url="https://github.com/Nachiket858/PyCodeML",  # Replace with your GitHub repo
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
        "numpy",  # Recommended for data handling
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",  # Change to Stable when production-ready
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="machine learning, regression, auto-model selection, data science",
    project_urls={
         # Replace with actual doc link
        "Source": "https://github.com/Nachiket858/PyCodeML",
       
    },
)
