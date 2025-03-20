import requests

# response = requests.get('https://api.example.com/data')
#
# # 检查请求是否成功
# if response.status_code == 200:
#     print('成功获取数据:', response.text)
# else:
#     print('请求失败，状态码:', response.status_code)

def call_http_tool(tool_info: {}, arguments: {}):
    # url = tool_info["domain"] if "domain" in tool_info else ""
    # params = tool_info["params"] if "params" in tool_info else ""
    # headers = tool_info["headers"] if "headers" in tool_info else ""
    # data = tool_info["data"] if "data" in tool_info else ""
    #
    # if tool_info["method"] == "GET":
    #     response = requests.get(url, params=params, headers=headers)
    # elif tool_info["method"] == "POST":
    #     response = requests.post(url, params=params, headers=headers, json=data)
    # else:
    #     raise Exception("ak/sk参数为空")
    #
    # response = requests.get(url, params=params, headers=headers, json=data)
    # if response.status == 200:
    #     return response.json()
    return {}