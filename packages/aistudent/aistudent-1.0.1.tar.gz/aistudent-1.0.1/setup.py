from setuptools import setup, find_packages

setup(
    name="aistudent",  
    version="1.0.1",  
    author="Babar Ahmad", 
    author_email="babar.ahmad@aumc.edu.pk",
    description="A simple AI utilities package for search, CSP, and games.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "networkx",
        "sortedcontainers",
        "pillow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
