from setuptools import setup, find_packages

setup(
    name="cmtqoutilities",    # Unique PyPI package name
    version="0.1.0b2",
    description="API for all cmtqo devices",    
    author="Sebastian Huber",
    author_email="huberse@phys.ethz.ch",
    url="https://gitlab.phys.ethz.ch/code/experiment/mm-runexperiment",
    packages=find_packages(include=["cmtqoutilities", "cmtqoutilities.utilities", "cmtqoutilities.utilities.*"]),
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.18.0",
        "requests>=2.25.0",
        "scipy>=1.5.0",
        "pyserial>=3.5",
        "zaber.serial>=0.9"
    ]
)