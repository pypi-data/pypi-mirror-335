from setuptools import setup, find_packages

setup(
    name="configurable-cl",
    version="0.1.7",
    author="Julien Rabault",
    author_email="julienrabault@icloud.com",
    description="This module provides classes and utilities for managing configurations, validating schemas, "
                "and creating Configurable objects from configuration data. It is particularly useful for AI "
                "applications where configurations can be complex and need to be validated at runtime.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JulienRabault/Configurable-cl",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "wheel",
        "PyYAML",
        "pytest",
        "typing-extensions"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
