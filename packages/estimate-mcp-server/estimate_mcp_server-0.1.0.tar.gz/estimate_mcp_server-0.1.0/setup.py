from setuptools import setup, find_packages

setup(
    name="estimate-mcp-server",
    version="0.1.0",
    description="견적서 분석 및 관리를 위한 MCP 서버",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Interior One Click",
    author_email="example@example.com",
    url="https://github.com/yourusername/estimate-mcp-server",
    packages=find_packages(include=['estimate_mcp_server', 'estimate_mcp_server.*']),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "firebase-admin>=6.2.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "estimate-mcp-server=estimate_mcp_server.main:start",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 