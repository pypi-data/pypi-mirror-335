# setup.py
from setuptools import setup, find_packages

setup(
    name="dbformatter",
    version="0.0.4",
    packages=find_packages(),  # Finds dbformatter/ with __init__.py
    description="A tool to format database entries",
    author="Bruteforcer",
    author_email="admin@example.com",
    url="https://github.com",  # Optional
    python_requires=">=3.6",
)