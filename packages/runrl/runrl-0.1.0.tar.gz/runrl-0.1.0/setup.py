from setuptools import setup, find_packages

setup(
    name="runrl",
    version="0.1.0",
    packages=find_packages(),
    description="A simple package to interface with RunRL",
    author="RunRL Team",
    author_email="team@runrl.com",
    url="https://runrl.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 