from setuptools import setup, find_packages

setup(
    name="potatopy",  
    version="1.0.0",
    author='potatoscript',
    author_email='potatoscript@hotmail.com',
    description='A simple Template for create python project',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/potatoscript/potatopy", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)