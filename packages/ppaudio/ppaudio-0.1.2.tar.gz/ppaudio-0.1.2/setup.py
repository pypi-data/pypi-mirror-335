from setuptools import setup, find_packages
import os

# 读取版本号
__version__ = "0.1.2"

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 获取依赖列表
def get_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ppaudio",
    version=__version__,
    author="Kid",
    author_email="kid@example.com",  # 请替换为您的邮箱
    description="An audio classification toolkit based on PaddlePaddle for detecting abnormal sounds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kid/ppaudio",  # 请替换为您的GitHub仓库地址
    packages=find_packages(include=['ppaudio', 'ppaudio.*']),
    include_package_data=True,
    package_data={
        'ppaudio': ['configs/*.yaml'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
    ],
    python_requires=">=3.7",
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'ppaudio-train=ppaudio.cli:train_cmd',
            'ppaudio-test=ppaudio.cli:test_cmd',
        ],
    },
    keywords=['audio', 'classification', 'deep learning', 'paddlepaddle', 'sound detection'],
)