from setuptools import setup, find_packages

setup(
    name="mypackage_test_one",
    version="0.1",
    packages=find_packages(),
    description="A simple greeting package",
    author="Fazil",
    author_email="fazil@example.com",
    url="https://github.com/shaik_fazil/mypackage",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
