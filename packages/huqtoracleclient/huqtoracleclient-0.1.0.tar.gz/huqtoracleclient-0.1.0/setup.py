# setup.py
from setuptools import setup, find_packages

setup(
    name="huqtoracleclient",               # Package name
    version="0.1.0",                 # Version
    description="A Python package for interacting with the HUQT Oracle exchange programmatically",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # author="Your Name",
    # author_email="your.email@example.com",
    # url="https://github.com/yourusername/my_package",  # Project URL
    packages=find_packages(),        # Automatically find packages in the directory
    include_package_data=True,
    classifiers=[                   # Optional metadata
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "grpcio",         # Ensure version compatibility
        "grpcio-tools",
        "setuptools>=64", 
        "wheel",
        # "protobuf>=3.X",      # Often not needed explicitly, but can be added if desired.
    ],
    python_requires=">=3.7",         # Minimum Python version
)