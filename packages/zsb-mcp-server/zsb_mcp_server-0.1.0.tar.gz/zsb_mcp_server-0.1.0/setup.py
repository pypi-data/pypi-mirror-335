from setuptools import setup, find_packages

setup(
    name="zsb_mcp_server",  # 包名
    version="0.1.0",  # 版本号
    author="Zhang Shenbin",  # 作者
    author_email="zhangshenbin7@sina.com",  # 作者邮箱
    description="A short description of your package",  # 简短描述
    # long_description=open("README.md").read(),  # 长描述（README 文件）
    long_description_content_type="text/markdown",  # 长描述格式
    url="https://github.com/yourusername/my_package",  # 项目主页
    packages=find_packages(),  # 自动发现包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",  # Python 版本要求
    install_requires=[  # 依赖项
        # "requests>=2.25.1",
    ],
)