from setuptools import setup, find_packages

setup(
    name="enci_mcp_server",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.18.0",
        "pandas>=1.0.0",
    ],
    author="mingyang",
    author_email="worklxh@gmail.com",
    description="enci_mcp_server",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)