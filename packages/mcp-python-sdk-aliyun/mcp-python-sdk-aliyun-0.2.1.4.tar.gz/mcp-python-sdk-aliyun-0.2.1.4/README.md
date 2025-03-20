

[//]: # (1. python3 -m venv myenv)

[//]: # (2. source myenv/bin/activate  激活虚拟环境)

[//]: # (3. pip3 install -r requirements.txt  安装依赖)

[//]: # (4. pyinstaller --onefile __main__.py --name mcp-server-aliyun-python-sdk)


# **说明**
mcp python sdk，用于适配阿里云服务注册中心开发的运行在客户端本地的mcp server。

整体方案：https://alidocs.dingtalk.com/i/nodes/gwva2dxOW4vRkd9DUqbedAnGJbkz3BRL

sdk使用方式：https://alidocs.dingtalk.com/i/nodes/gvNG4YZ7Jnxop15OCnEXnDqEW2LD0oRE

# 使用方式概览
两种使用方式。

## 方式一：直接使用源码

源码clone到本地后，创建python虚拟环境，从requirements.txt文件安装依赖，然后在支持cline的客户端启动客户端即可。

详情参照[sdk使用文档](https://alidocs.dingtalk.com/i/nodes/gvNG4YZ7Jnxop15OCnEXnDqEW2LD0oRE)

## 方式二：打包可执行文件

源码clone到本地后，创建python虚拟环境，从requirements.txt文件安装依赖，使用pyinstaller打包成可执行文件，然后在支持cline的客户端通过该可执行文件启动即可。

文档[sdk使用文档](https://alidocs.dingtalk.com/i/nodes/gvNG4YZ7Jnxop15OCnEXnDqEW2LD0oRE)中有已经打包好的可执行文件。



