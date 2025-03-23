import os

import subprocess
import sys
import importlib


def subModules():
    # 获取模块的根目录
    the_dir = os.path.dirname(os.path.abspath(__file__))

    # 列出所有子目录和文件
    contents = os.listdir(the_dir)

    # 过滤出包含 __init__.py 文件的子目录
    submodules = [
        name for name in contents
        if os.path.isdir(os.path.join(the_dir, name)) and
           os.path.isfile(os.path.join(the_dir, name, '__init__.py'))
    ]

    return submodules



def insModuleReqs(module_name):
    # 安装子模块的依赖
    packages = getattr(importlib.import_module(f'cjptools.{module_name}'), "reqs")
    """Install packages using pip."""
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
