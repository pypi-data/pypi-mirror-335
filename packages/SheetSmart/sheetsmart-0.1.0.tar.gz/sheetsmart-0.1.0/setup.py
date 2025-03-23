from setuptools import setup, find_packages

setup(
    name="SheetSmart",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Bhuvanesh M",
    author_email="bhuvaneshm.developer@gmail.com",
    description="A Python package named SheetSmart.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bhuvanesh-m-dev/sheetsmart",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
