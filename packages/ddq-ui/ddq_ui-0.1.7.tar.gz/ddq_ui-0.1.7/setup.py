from setuptools import setup, find_packages
import os

setup(
    name="ddq_ui",
    version="0.1.7",
    packages=find_packages(exclude=['tests*']),  # 排除测试包
    package_data={
        '': ['*.json', '*.yaml', '*.yml', '*.txt'],  # 包含所有包中的这些文件
    },
    install_requires=[
        # tkinter 是 Python 标准库，不需要在这里指定
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    test_suite='tests',
    python_requires='>=3.6',
    description="DDQ UI Framework - 一个灵活的 UI 框架，支持多种后端实现",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="DDQ",
    author_email="ddq@example.com",  # 请替换为您的实际邮箱
    url="https://github.com/ddq/ddq_ui",  # 请替换为您的实际仓库地址
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords='ui, tkinter, framework, widgets',
    project_urls={
        'Documentation': 'https://github.com/ddq/ddq_ui#readme',
        'Source': 'https://github.com/ddq/ddq_ui',
        'Tracker': 'https://github.com/ddq/ddq_ui/issues',
    },
) 