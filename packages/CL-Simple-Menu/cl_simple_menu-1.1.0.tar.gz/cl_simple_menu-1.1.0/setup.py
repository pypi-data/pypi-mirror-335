from setuptools import setup, find_packages

setup(
    name="CL-Simple-Menu",  # 包名称
    version="1.1.0",  # 包版本号
    author="Kono_Yalu",  # 作者名称
    author_email="327112257@qq.com",  # 联系邮箱
    description="A lightweight Python library for interactive command-line menus.",
    long_description=open("README.md", encoding="utf-8").read(),  # 从 README.md 中加载描述
    long_description_content_type="text/markdown",
    url="https://github.com/dingzhen-vape/SimpleMenu",  # 项目的仓库地址
    packages=find_packages(),  # 自动发现包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        "pywin32",
        "pygetwindow",
    ],
    python_requires=">=3.6",  # 支持的 Python 版本
)
