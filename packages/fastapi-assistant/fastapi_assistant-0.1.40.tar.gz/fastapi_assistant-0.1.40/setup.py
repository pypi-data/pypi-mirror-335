import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name="fastapi_assistant",  # 模块名称
    version="0.1.40",  # 当前版本
    author="lxshen",  # 作者w
    author_email="lxshen613@163.com",  # 作者邮箱
    description="fastapi脚手架，封装了基本curd、excel处理、异常、仿照django实现的get_or_one,create_or_update",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    url="https://gitee.com/ileona/fastapi-assistant.git",  # 模块github地址
    # packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    packages=setuptools.find_namespace_packages(include=["fastapi_assistant", "fastapi_assistant.*"], ),
    include_package_data=True,

    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
        'fastapi>=0.63.0',
        'pandas>=1.3.0',
        'orjson>=3.5.2',
        'sqlalchemy>=1.3.22',
        'sqlalchemy<2.0.0',
        'uvicorn>=0.13.4',
        'setuptools>=41.6.0',
        'pydantic>=1.8.1',
        'starlette>=0.13.6',
        'pymysql>=0.9.3',
        'styleframe>=4.1',
        'pytest>=4.1',
        'APScheduler>=3.8.0',
        'numpy>=1.20.0',
        'openpyxl>=3.1.2'
    ],
    python_requires='>=3.8.0',
)