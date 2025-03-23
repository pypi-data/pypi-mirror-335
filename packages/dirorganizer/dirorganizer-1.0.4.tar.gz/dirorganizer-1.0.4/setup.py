from setuptools import setup, find_packages

setup(
    name="dirorganizer",  # Unique package name
    version="1.0.4",
    author="Rahul Verma",
    author_email="rahulverma.1.2005@gamil.com",
    description="A simple CLI tool to organize files by extensions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SudoRV/fileorganizer",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "arrange=dirorganizer.arrange_files:main",
        ],
    },
)
