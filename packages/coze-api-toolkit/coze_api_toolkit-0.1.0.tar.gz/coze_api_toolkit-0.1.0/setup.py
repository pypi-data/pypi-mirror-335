"""
Coze API 工具包安装配置
"""
import os
from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取依赖
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="coze-api-toolkit",
    version="0.1.0",
    author="Coze API Toolkit Team",
    author_email="your-email@example.com",
    description="基于 Coze 工作流 API 的简化 Python 工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/coze-api-toolkit",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "coze_api_toolkit": ["config/*.json"],
    },
) 