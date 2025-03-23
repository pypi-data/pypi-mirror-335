# setup.py
from setuptools import setup, find_packages

setup(
    name="featuremesh",    # Replace with your desired package name
    version="0.0.1",             # Start with a pre-release version
    author="FeatureMesh Team",
    author_email="nic@featuremesh.com",
    description="FeatureMesh client for python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://featuremesh.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)