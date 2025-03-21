from setuptools import setup, find_packages # type: ignore

setup(
    name="expense_report",
    version="0.0.1",
    author="Hemadhri Govindaraju",
    author_email="hemadhri0107003@gmail.com",
    description="A simple library to generate CSV and PDF expense reports.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Hemadhri01/expense_report_pkg",
    packages=find_packages(),
    install_requires=[
        "reportlab",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
