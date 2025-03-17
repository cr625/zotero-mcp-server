from setuptools import setup, find_packages

setup(
    name="zotero-mcp-server",
    version="0.1.0",
    description="A Model Context Protocol server for Zotero integration",
    author="AI Ethical DM Team",
    author_email="user@example.com",
    packages=find_packages(),
    install_requires=[
        "pyzotero>=1.5.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "jsonschema>=4.17.0",
    ],
    entry_points={
        "console_scripts": [
            "zotero-mcp-server=src.server:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
