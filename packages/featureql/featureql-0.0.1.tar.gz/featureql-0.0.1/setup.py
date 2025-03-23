# setup.py
from setuptools import setup, find_packages

setup(
    name="featureql",    
    version="0.0.1",          
    author="FeatureQL Team",
    author_email="nic@featuremesh.com",
    description="FeatureQL client for python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://featureql.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)