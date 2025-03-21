from setuptools import setup, find_packages

setup(
    name="tpconfig",
    version="0.1.2",
    author="Nopaque Limited",
    author_email="info@nopaque.co.uk",
    description="Configuration management for TotalPath services",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nopaque/tpconfig",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "boto3>=1.37.8",
    ],
)