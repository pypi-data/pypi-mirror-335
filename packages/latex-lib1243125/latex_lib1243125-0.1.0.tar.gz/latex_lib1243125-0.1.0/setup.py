from setuptools import setup, find_packages

setup(
    name="latex_lib1243125",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="latex_lib",
    author="latex_lib",
    author_email="latex_libl@latex_lib.com",
    url="https://github.com/no",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)