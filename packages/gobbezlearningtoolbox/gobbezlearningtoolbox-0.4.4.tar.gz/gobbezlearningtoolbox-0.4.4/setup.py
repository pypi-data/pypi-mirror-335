from setuptools import setup, find_packages

setup(
    name="gobbezlearningtoolbox",
    version="0.4.4",
    author="Andrea Gobbetti",
    author_email="a.gobbez@hotmail.it",
    description="My learning toolbox, with every code that i have studied",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gobbez/learningtoolbox",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
