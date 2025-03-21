import requests

def call_http_tool(tool_info: {}, arguments: {}):
    if "protocol" not in tool_info or not isinstance(tool_info["protocol"], dict):
        raise Exception("openapi工具调用信息protocol不可为空")
    protocol = tool_info["protocol"]

    url = protocol["url"] if "url" in protocol else ""
    params = arguments["params"] if "params" in arguments else ""
    headers = arguments["headers"] if "headers" in arguments else ""
    data = arguments["data"] if "data" in arguments else ""

    if protocol["methodType"].upper() == "POST":
        response = requests.post(url, headers=headers, json=data, verify=False)
    else:
        response = requests.get(url, params=params, headers=headers, verify=False)

    if response.status == 200:
        return response.json()
    return {}


if __name__ == '__main__':
    res = call_http_tool(tool_info={
        "protocol": {
            "methodType": "get",
            "url": "https://pre-ai-assistant-management.aliyun-inc.com/mcp/server/list"
        }
    }, arguments={
    })
    print(res)
