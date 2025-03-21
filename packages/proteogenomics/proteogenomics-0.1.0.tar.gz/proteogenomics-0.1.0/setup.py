from setuptools import setup, find_packages

# Read long description safely
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="proteogenomics",  # Your package name
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy", 
        "pandas", 
        "matplotlib", 
        "plotly", 
        "re", 
        "seaborn", 
        "os", 
        "time"
    ],
    entry_points={
        "console_scripts": [
            "proteogenomics=proteogenomics.proteogenomic:main",  # Adjust based on your script structure
        ],
    },
    author="Sethupathy Selvaraj, Arunachalam A",
    author_email="masssanjay85@gmail.com",
    description="A CLI tool for proteogenomics analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sethuakasanji/proteogenomics-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
)
