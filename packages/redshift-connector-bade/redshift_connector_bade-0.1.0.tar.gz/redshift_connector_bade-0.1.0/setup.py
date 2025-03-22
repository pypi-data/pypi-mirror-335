#!/usr/bin/env python
# coding: utf-8

# In[1]:


from setuptools import setup, find_packages

setup(
    name="redshift_connector_bade",  # 套件名稱
    version="0.1.0",            # 版本號
    author="Hans, Roy",
    author_email="royhsu1012@hmail.com",
    description="A simple connector for Amazon Redshift using JDBC",
    long_description=open("README.md").read(),  # 你的 README 文件
    long_description_content_type="text/markdown",
    url="https://github.com/royhsu1012/redshift_connector",  # 你的 GitHub 地址
    packages=find_packages(),  # 自動尋找所有模組
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # 這個根據你的授權許可來修改
        "Operating System :: OS Independent",
    ],
    install_requires=[         # 必要的依賴包
        "jpype1",
        "jaydebeapi",
        "pandas",
        "requests",  # 如果需要下載 GitHub 檔案，則需要安裝 requests
    ],
    python_requires=">=3.6",   # 支援的 Python 版本
)


# In[ ]:




