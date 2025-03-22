from setuptools import setup, find_packages

setup(
    name='dut_segment',  # 包名称
    version='0.1.0',  # 包版本
    packages=find_packages(),  # 自动找到所有模块
    entry_points={  # 让你的项目能在命令行运行
        'console_scripts': [
            'dut_segment=dut_segment.main:__init__',  # 指定运行入口
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
