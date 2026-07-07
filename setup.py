from setuptools import setup, find_packages

setup(
    name="warehouse-simulation",
    version="1.0.0",
    description="Warehouse Operations Simulation and Optimization Using SimPy",
    packages=find_packages(),
    install_requires=[
        "simpy>=4.0.1",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "matplotlib>=3.6.0",
    ],
    python_requires=">=3.8",
)
