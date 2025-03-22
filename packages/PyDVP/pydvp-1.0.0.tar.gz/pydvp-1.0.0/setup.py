from setuptools import setup, find_packages

setup(
    name="PyDVP",  # Your package name
    version="1.0.0",
    author="Dexon Systems Ltd.",
    author_email="sales@dexonsystems.com",
    description="A DEXON DIVIP Python library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://dexonsystems.com/contact",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
