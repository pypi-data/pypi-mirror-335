import json
import traceback

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server

import aiohttp

from .hsf_caller import call_hsf_tool
from .openapi_caller import call_openapi_tool
from .http_caller import call_http_tool
from ..utils.log_utils import init_logger, log_info, log_error
from ..utils.utils import generate_custom_trace_id

headers = {"User-Agent": "ai_copilot"}
# tool_list_url = 'http://localhost:7001/api/mcp/tool/list?serverCode='
tool_list_url = 'https://ai-assistant-management.aliyun-inc.test/api/mcp/tool/list?serverCode='
# tool_list_url = 'https://pre-ai-assistant-management.aliyun-inc.com/api/mcp/tool/list?serverName='


async def fetch_tool_list(server_name: str):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        response = await session.get(tool_list_url+server_name, headers=headers)
        if response.status == 200:
            return await response.json()
        return {}


@click.command()
@click.option("--server_name", default="default", help="指定服务端的名称")
@click.option("--log_file", default="default", help="指定mcp server日志输出的位置")
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(server_name: str, log_file: str, port: int, transport: str) -> int:
    logger = init_logger(log_file)
    log_info(logger, f"mcp server runs, server_name: {server_name}")
    app = Server(server_name)

    @app.call_tool()
    async def fetch_tool(
            name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        trace_id = generate_custom_trace_id()
        log_info(logger, f"{trace_id}|call tool, server_name: {server_name}, tool_name: {name}, args: {arguments}")

        # 查询tool list
        try:
            tool_list_data = await fetch_tool_list(server_name=server_name)
        except Exception as e:
            log_info(logger, f"{trace_id}|远端服务请求失败[tool:{name}]: {traceback.format_exc()}")
            raise ValueError(f"远端服务请求失败[tool:{name}]")
        if "data" not in tool_list_data or tool_list_data["data"] is None or "tools" not in tool_list_data["data"]:
            log_info(logger, f"{trace_id}|远端服务返回结果异常[tool:{name}]: {tool_list_data}")
            raise ValueError(f"远端服务返回结果异常[tool:{name}]")

        # 找到具体的工具
        tool_info = None
        for item in tool_list_data["data"]["tools"]:
            if item["toolCode"] == name:
                tool_info = item
                break
        if tool_info is None:
            log_info(logger, f"{trace_id}|远端服务返回结果异常[tool:{name}]: {tool_list_data}")
            raise ValueError(f"找不到工具[tool:{name}]")

        # 工具调用
        try:
            log_info(logger, f"{trace_id}|begin call tool, server_name: {server_name}, tool_name: {name}, args: {arguments}, tool_info: {tool_info}")
            protocolType = tool_info["protocolType"]
            if protocolType == "OPENAPI":
                response = call_openapi_tool(tool_info=tool_info, arguments=arguments)
                log_info(logger, f"{trace_id}|call openapi tool, res: {response}")
            elif protocolType == "HTTP":
                response = call_http_tool(tool_info=tool_info, arguments=arguments)
                log_info(logger, f"{trace_id}|call http tool, res: {response}")
            elif protocolType == "HSF":
                response = call_hsf_tool(tool_info=tool_info, arguments=arguments)
                log_info(logger, f"{trace_id}|call hsf tool, res: {response}")
            else:
                log_info(logger, f"{trace_id}|工具服务类型配置错误[protocolType:{protocolType}]")
                raise ValueError(f"{trace_id}|工具服务类型配置错误[protocolType:{protocolType}]")
            log_info(logger, f"{trace_id}|call tool, server_name: {server_name}, tool_name: {name}, res: {response}")

            # 返回工具结果，含结果描述信息
            return [types.TextContent(type="text", text=json.dumps(
                {"result": response, "resultDesc": tool_info["resultDesc"] if "resultDesc" in tool_info else {}},
                ensure_ascii=False))]
        except Exception as e:
            print(traceback.format_exc())
            log_error(logger, f"{trace_id}|工具调用失败[tool:{name}]: {str(e)}")
            raise ValueError(f"工具调用失败[tool:{name}]: {str(e)}")


    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        trace_id = generate_custom_trace_id()
        log_info(logger, f"{trace_id}|fetch tool list，server_name: {server_name}")
        try:
            # 获取tool列表
            tool_list_data = await fetch_tool_list(server_name=server_name)
            log_info(logger, f"{trace_id}|fetch tool list，server_name: {server_name}, res: {json.dumps(tool_list_data, ensure_ascii=False)}")

            # 返回tool列表
            if "data" not in tool_list_data or tool_list_data["data"] is None:
                return []
            else:
                res = []
                for item in tool_list_data["data"]["tools"]:
                    res.append(types.Tool(
                        name=item["toolCode"],
                        description=item["description"],
                        inputSchema=item["paramJsonSchema"] if 'paramJsonSchema' in item else {"type": "object", "required": [], "properties": {}}
                    ))
                return res
        except Exception as e:
            print(traceback.format_exc())
            log_info(logger, f"{trace_id}|fetch tool list，server_name: {server_name}, res: {traceback.format_exc()}")
        return []

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                    request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0
