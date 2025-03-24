from setuptools import setup, find_packages

setup(
    name="ilovesyd",
    version="1.4.0",
    author="KrishVi",
    author_email="krish@ilovesyd.xyz",
    description="A Python wrapper for ilovesyd.xyz API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KrishhVii/ilovesyd",  # Change to your repo
    packages=find_packages(),
    install_requires=[
        "aiohttp",  # Since it's async
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
