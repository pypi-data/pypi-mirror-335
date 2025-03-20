from setuptools import setup, find_packages

setup(
    name="monetary-classifier",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.17.0",
        "scikit-learn>=0.24.0",
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
    ],
    extras_require={
        "xgboost": ["xgboost>=1.0.0"],
        "lightgbm": ["lightgbm>=3.0.0"],
        "catboost": ["catboost>=0.24.0"],
        "dev": [
            "pytest>=6.0.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A scikit-learn compatible package for classification with monetary outcomes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/monetary-classifier",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)
