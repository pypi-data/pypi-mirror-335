# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages
from openai_redis_vectorstore.version import VERSION

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]


setup(
    name="openai-redis-vectorstore",
    version=VERSION,
    description="基于RedisStack向量数据库，集成embeddings和rerank模型，支持二阶段召回，支持添加和删除等管理功能。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rRR0VrFP",
    maintainer="rRR0VrFP",
    license="Apache License, Version 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["openai-redis-vectorstore"],
    packages=find_packages("."),
    install_requires=requires,
    zip_safe=False,
    include_package_data=True,
)
