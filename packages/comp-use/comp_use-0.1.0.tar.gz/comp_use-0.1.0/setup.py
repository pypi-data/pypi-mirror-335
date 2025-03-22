from setuptools import setup, find_packages

setup(
    name="comp-use",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Xiangyi Li",
    author_email="xiangyi@benchflow.ai",
    description="A placeholder package for comp-use",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/placeholder/comp-use",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 