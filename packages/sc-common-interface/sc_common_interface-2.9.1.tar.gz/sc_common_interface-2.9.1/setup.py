from setuptools import setup, find_packages

setup(
    name='sc_common_interface',
    version='2.9.1',
    description='SC贴文销售公用的接口',
    author='river',
    packages=find_packages(),
    install_requires=[
    "requests>=2.0.0",
    "jsonpath>=0.82"
             ],
)

