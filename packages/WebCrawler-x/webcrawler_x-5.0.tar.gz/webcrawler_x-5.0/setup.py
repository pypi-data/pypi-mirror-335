from distutils.core import  setup
import setuptools


packages = ['WebCrawler_x']# 唯一的包名，自己取名
setup(name='WebCrawler_x',
	version='5.0',
	author='jackson_tao',
    packages=packages,
    package_dir={'requests': 'requests'},)
