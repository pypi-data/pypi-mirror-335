from setuptools import setup, find_packages

setup(
    name="simplecalculator-ganesan",
    version="0.2.0",
    author="Ganesan Selvaraj",
    author_email="ganesanluna@yahoo.in",
    description="A simple calculator package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
