from setuptools import setup, find_packages

setup(
    name="liberal_alpha",  # 你的 PyPI 包名
    version="0.1.3",  # 初始版本号
    author="capebaralabs",  # 你的名字
    author_email="donny@capybaralabs.xyz",  # 你的邮箱
    description="Liberal Alpha Python SDK for interacting with gRPC-based backend",
    long_description=open("README.md", encoding="utf-8").read(),  # 读取 README 作为 PyPI 介绍
    long_description_content_type="text/markdown",  # 说明内容格式
    url="https://github.com/capybaralabs-xyz/Liberal_Alpha",  # 你的 GitHub 地址
    packages=find_packages(exclude=["tests", "tests.*"]),  # 自动找到所有 Python 包
    include_package_data=True, 
    install_requires=[
        "grpcio>=1.40.0",  # 你的 SDK 依赖项
        "protobuf>=3.20.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 你的 SDK 适用的 Python 版本
)