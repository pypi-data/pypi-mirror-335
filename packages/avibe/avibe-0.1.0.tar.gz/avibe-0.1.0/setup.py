# setup.py

from setuptools import setup, find_packages

setup(
    name="avibe",
    version="0.1.0",
    description="Utility for executing python async functions everywhere the same way - scripts, notebooks, etc.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Zach Blumenfeld",
    author_email="zblumenf@gmail.com",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "nest-asyncio",
    ],
    extras_require={
        "test": [  # Test-specific dependencies
            "unittest",  # Built-in library if using unittest (optional to specify here)
            "nbconvert",  # For running notebooks as tests
            "nbformat",  # Parsing Jupyter Notebooks
            "jupyter",  # Supporting Jupyter integration
            "pytest",  # An alternative test runner
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

