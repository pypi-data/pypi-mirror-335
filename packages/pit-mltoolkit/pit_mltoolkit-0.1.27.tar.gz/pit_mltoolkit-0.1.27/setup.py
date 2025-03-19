# setup.py
from setuptools import setup, find_packages

setup(
    name="pit-mltoolkit",
    version="0.1.27",  # Update this on each release
    author="PepkorIT MLE",
    author_email="neilslab@pepkorit.com",
    description="Tools and functions for machine learning engineering and data science",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pit-mle/mltoolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
    ],
)
