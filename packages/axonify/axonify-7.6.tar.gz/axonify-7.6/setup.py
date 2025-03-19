from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axonify",
    version="7.6",
    description="Axonify is a versatile Python library designed to provide a comprehensive suite of utilities for system operations, file management, and logging. It is particularly useful for developers who need to perform complex tasks with minimal setup and overhead. Axonify includes advanced logging capabilities, file operations, system information retrieval, and more, making it a powerful tool for a wide range of applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  
    python_requires=">=3",
    install_requires=["requests", "pybase64", "importlib"],
)