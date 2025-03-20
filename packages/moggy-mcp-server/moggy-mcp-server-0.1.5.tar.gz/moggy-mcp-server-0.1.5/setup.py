from setuptools import setup, find_packages

setup(
    name="moggy-mcp-server",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.4.1",
    ],
    author="mingyang",
    author_email="worklxh@gmail.com",
    description="MCP Server for Moggy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
            'moggy-mcp-server=sample_mcp:main',
        ],
    },
)