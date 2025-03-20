from setuptools import setup, find_packages

setup(
    name='mcp-python-sdk-aliyun', # 替换为你的包名
    version='0.2.1.4',  # 版本号
    # packages=find_packages(),
    packages=['src', 'src.aliyun', 'src.utils', 'src.demo'],
    install_requires=[
        # 列出你的包依赖的所有其他包
        "alibabacloud-tea-openapi>=0.3.13",
        "anyio>=4.8.0",
        "click>=8.1.8",
        "httpx>=0.28.1",
        "httpx-sse>=0.4.0",
        "mcp>=1.3.0",
    ],
    entry_points={
        'console_scripts': [
            'mcp-python-sdk-aliyun = src.aliyun.server:main'
            # 如果你的包包含可执行脚本，这里可以定义它们
        ],
    },
    author='Chen',
    author_email='872679742@qq.com',
    description='mcp python sdk aliyun',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://example.com',
    classifiers=[
        # 分类器帮助PyPI对你的包进行分类
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
)