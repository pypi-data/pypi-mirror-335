from setuptools import setup, find_packages

setup(
    name="pydbfi",
    version="0.1.5", 
    author="ivk",
    author_email="leorivk@gmail.com",
    description="DB증권 API Python SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/leorivk/pydbfi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
)
