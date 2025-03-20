
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_util import models as util_models


def call_openapi_tool(tool_info: {}, arguments: {}):
    ak = ""
    sk = ""
    if "ak" in arguments:
        ak = arguments["ak"]
    elif "AK" in arguments:
        ak = arguments["AK"]
    if "sk" in arguments:
        sk = arguments["sk"]
    elif "SK" in arguments:
        sk = arguments["SK"]
    if "" in (ak, sk):
        raise Exception("ak/sk参数为空")

    if "protocol" not in tool_info or not isinstance(tool_info["protocol"], dict):
        raise Exception("openapi工具调用信息protocol不可为空")
    protocol = tool_info["protocol"]

    endpoint = protocol["domain"] if "domain" in protocol else ""
    action = protocol["action"] if "action" in protocol else ""
    version = protocol["version"] if "version" in protocol else ""
    method = "POST"

    if "" in (endpoint, action, version, method):
        raise Exception("openapi参数不可为空")

    query = OpenApiUtilClient.query(arguments)

    # 从环境变量中获取访问密钥
    config = open_api_models.Config(
        access_key_id=ak,
        access_key_secret=sk,
        endpoint=endpoint
    )
    client = OpenApiClient(config)
    params = open_api_models.Params(
        style='RPC',  # API风格
        version=version,  # API版本号
        action=action,  # API 名称
        method=method,  # 请求方法
        pathname='/',  # 接口 PATH
        protocol='HTTPS',  # 接口协议,
        auth_type='AK',
        req_body_type='json',  # 接口请求体内容格式,
        body_type='json'  # 接口响应体内容格式,
    )

    # 创建API请求对象
    request = open_api_models.OpenApiRequest(
        query=query,
    )
    # 创建运行时选项对象
    runtime = util_models.RuntimeOptions()
    # 发起API调用
    response = client.call_api(params, request, runtime)
    return response

