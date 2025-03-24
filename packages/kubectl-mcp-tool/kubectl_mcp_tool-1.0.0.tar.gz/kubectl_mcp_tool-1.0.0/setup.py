from setuptools import setup, find_packages

setup(
    name="kubectl-mcp-tool",
    version="1.0.0",
    description="A Model Context Protocol (MCP) server for Kubernetes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rohit Ghumare",
    author_email="ghumare64@gmail.com",
    url="https://github.com/rohitg00/kubectl-mcp-server",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "kubernetes>=28.1.0",
        "rich>=13.0.0",
        "aiohttp>=3.8.0",
        "aiohttp-sse>=2.1.0",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "urllib3>=2.1.0",
        "websocket-client>=1.7.0",
        "jsonschema>=4.20.0",
        "cryptography>=42.0.2",
    ],
    dependency_links=[
        "git+https://github.com/modelcontextprotocol/python-sdk.git#egg=mcp"
    ],
    entry_points={
        "console_scripts": [
            "kubectl-mcp=kubectl_mcp_tool.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.9",
)
