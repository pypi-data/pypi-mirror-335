from setuptools import setup, find_packages

setup(
    name="minicode",  # 包名
    version="1.0.0",  # 版本号
    author="Lv Wenlong",  # 作者
    author_email="a13898004158@outlook.com",  # 作者邮箱
    description="A simple encrypt tool using Python.",  # 简短描述
    #long_description=open("README.md").read(),  # 从 README.md 读取长描述
    long_description_content_type="text/markdown",  # 长描述的格式
    url="",  # 项目主页
    packages=find_packages(),  # 自动发现包
    install_requires=[],  # 依赖项
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Python 版本要求
    entry_points={
        'console_scripts': [
            'mmake=mmake.__main__:run',  # 定义命令行入口
        ],
    },
)
