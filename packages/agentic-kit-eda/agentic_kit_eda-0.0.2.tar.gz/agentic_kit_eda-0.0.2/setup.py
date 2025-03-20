from pathlib import Path

from setuptools import setup, find_packages

setup(
    name='agentic-kit-eda',
    version="0.0.2",
    author="manson",
    author_email="manson.li3307@gmail.com",
    description='EDA agent framework based on Langgraph',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',  # 添加开发状态分类器
        'Intended Audience :: Developers',  # 添加目标受众分类器
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10',
    # todo: update requirements
    install_requires=[
        "agentic_kit_core",
        "langchain_community==0.3.20",
        "langchain_core==0.3.45",
        "langgraph==0.3.16",
        "pydantic==2.10.6",
        "redis_lock==0.2.0",
        "setuptools==75.1.0",
        "starlette==0.46.1",
        "typing_extensions==4.12.2",
        "websocket_client==1.8.0"
    ],
    keywords=['AI', 'LLM', 'Agent'],
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '.csv']
    },
)
