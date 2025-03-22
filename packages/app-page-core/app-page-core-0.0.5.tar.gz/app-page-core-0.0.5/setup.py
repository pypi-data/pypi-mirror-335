import setuptools
from pathlib import Path

package_name = "app-page-core"
version = '0.0.5'
long_description = open("README.md", encoding="utf-8").read()
# 读取 requirements.txt 文件
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=package_name,
    version=version,
    author="xiaohuicat",  # 作者名称
    author_email="1258702350@qq.com", # 作者邮箱
    description="python page application framework", # 库描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaohuicat/python-app-page-core", # 库的官方地址
    license="MIT",
    packages=["app_page_core"],
    install_requires=requirements,
    zip_safe=False,
)