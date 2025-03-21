from setuptools import setup
import tomli

# Read dependencies from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject_data = tomli.load(f)

# Get dependencies from pyproject.toml
dependencies = pyproject_data["project"]["dependencies"]

setup(
    name="kaggle-mcp",
    version="0.1.0",
    description="MCP server for Kaggle APIs",
    author="Dixing Xu",
    author_email="i@dex.moe",
    packages=["kaggle_mcp"],
    python_requires=">=3.10",
    install_requires=dependencies,
    entry_points={
        "console_scripts": [
            "kaggle-mcp=kaggle_mcp.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["kaggle", "openapi", "mcp", "llm", "claude", "ai", "tools", "api"],
    project_urls={
        "Homepage": "https://github.com/dexhunter/kaggle-mcp",
        "Documentation": "https://github.com/dexhunter/kaggle-mcp#readme",
        "Bug Tracker": "https://github.com/dexhunter/kaggle-mcp/issues",
        "PyPI": "https://pypi.org/project/kaggle-mcp/",
        "Source Code": "https://github.com/dexhunter/kaggle-mcp",
        "Changelog": "https://github.com/dexhunter/kaggle-mcp/blob/main/CHANGELOG.md",
    },
)
