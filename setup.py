from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="zotero-mcp-server",
    version="0.1.0",
    author="Chris",
    author_email="chris@example.com",
    description="A Model Context Protocol server for Zotero integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/zotero-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "zotero-mcp-server=src.server:main",
        ],
    },
)
