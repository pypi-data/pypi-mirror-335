#!/usr/bin/env python
# -*- coding:utf-8 -*-


#############################################
# File Name: setup.py
# Author: Cai Jianping
# Mail: jpingcai@163.com
# Created Time:  2025-03-23 10:41:19
#############################################


from setuptools import setup, find_packages

setup(
    name="cjptools",
    version="0.2.3",
    keywords=["database", "localServer"],
    description="My Personal Toolkit",
    long_description="My Personal Toolkit",
    license="MIT Licence",
    author="Cai Jianping",
    author_email="jpingcai@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["numpy"],
    entry_points={"console_scripts": ["s2t=cjptools.lang_trans:simple2tradition_main", "clnah=cjptools.arxiv:clean_html_main", "genqr=cjptools.qrcode:gen_main"]}
)
