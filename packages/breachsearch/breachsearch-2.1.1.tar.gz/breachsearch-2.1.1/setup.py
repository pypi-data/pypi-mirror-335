from setuptools import setup, find_packages

setup(
    name="breachsearch",
    version="2.1.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "breachsearch=breachsearch.main:main",
        ],
    },
    author="Tintumon",
    author_email="",
    description="A tool to check if an data is part of a data breach.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/appuachu/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
