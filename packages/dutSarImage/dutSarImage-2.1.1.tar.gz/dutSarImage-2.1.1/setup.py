# from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='dutSarImage',
    packages=['dutSarImage'],  # this must be the same as the name above
    version='2.1.1',
    entry_points={  # 让你的项目能在命令行运行
        'console_scripts': [
            'dutSarImage=dutSarImage.main:__init__',  # 指定运行入口
        ],
    },
    include_package_data=True,
    description='Algorithms for blackbox falsification of convolutional neural networks',
    author='Qyy',
    keywords=['testing', 'safety', 'deep learning', 'computer vision'],  # arbitrary keywords
    classifiers=[],
)
