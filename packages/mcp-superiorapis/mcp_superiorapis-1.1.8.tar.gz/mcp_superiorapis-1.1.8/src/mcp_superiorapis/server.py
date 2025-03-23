import asyncio
import json
import aiohttp
import os
import sys
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
from typing import Any, Dict, Optional, Union, List, Tuple, get_origin, get_args

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("mcp-superiorapis")

# Get credentials from environment variables
TOKEN = os.getenv("TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")


# Add this check at the top of your file
print(f"Running environment: Python {sys.version}", file=sys.stderr)
print(f"TOKEN environment variable: {'set (length: ' + str(len(TOKEN)) + ')' if TOKEN else 'not set'}", file=sys.stderr)
print(f"APPLICATION_ID environment variable: {'set (' + APPLICATION_ID + ')' if APPLICATION_ID else 'not set'}", file=sys.stderr)


def flatten_enum(schema):
    if not isinstance(schema, dict):
        return schema

    schema = schema.copy()
    properties = schema.get('properties', {})

    for prop_name, prop in properties.items():
        # 遞迴處理 nested object
        if prop.get('type') == 'object':
            schema['properties'][prop_name] = flatten_enum(prop)

        # 遞迴處理 array 裡面的 item
        elif prop.get('type') == 'array':
            items = prop.get('items', {})
            # 針對 items 內的 enum 處理
            if 'enum' in items:
                enum_val = items['enum']
                original_desc = prop.get('description', '')

                if isinstance(enum_val, dict):
                    enum_str = ', '.join(f"{k}: {v}" for k, v in enum_val.items())
                    prop['description'] = f"{original_desc} | Enum: {enum_str}"
                elif isinstance(enum_val, list):
                    enum_str = ', '.join(str(e) for e in enum_val)
                    prop['description'] = f"{original_desc} | 選項: {enum_str}"

                # 移除 items 內的 enum
                prop['items'].pop('enum', None)

            # 如果 items 也是 object 結構要繼續遞迴
            if isinstance(items, dict):
                prop['items'] = flatten_enum(items)

        # 處理直接在 property 上的 enum
        if 'enum' in prop:
            enum_val = prop['enum']
            original_desc = prop.get('description', '')

            if isinstance(enum_val, dict):
                enum_str = ', '.join(f"{k}: {v}" for k, v in enum_val.items())
                prop['description'] = f"{original_desc} | Enum: {enum_str}"
            elif isinstance(enum_val, list):
                enum_str = ', '.join(str(e) for e in enum_val)
                prop['description'] = f"{original_desc} | 選項: {enum_str}"

            # 移除 enum
            prop.pop('enum')

    return schema
async def fetch_api_data():
    if not TOKEN or not APPLICATION_ID:
        raise ValueError("TOKEN and APPLICATION_ID environment variables must be set")
    
    async with aiohttp.ClientSession() as session:
        url = "https://superiorapis-creator.cteam.com.tw/manager/module/plugins/list_v2"
        headers = {
            "token": f"{TOKEN}", 
            "Content-Type": "application/json"
        }
        params = {
            "application_id": APPLICATION_ID
        }
        async with session.post(url, headers=headers, json=params) as response:
            if response.status != 200:
                raise Exception(f"API request failed with status {response.status}")
            return await response.json()


async def register_tools():
    plugins_data = await fetch_api_data()
    #print(result)  # 你要印結果可以放這
    functions = []
    for plugin_item in plugins_data['plugins']:
        plugin = plugin_item['plugin']
        model_name = plugin.get('name_for_model')
        plugin_desc = plugin.get('description_for_model', '')
        paths = plugin.get('interface', {}).get('paths', {})

        for path, methods in paths.items():
            for http_method, method_info in methods.items():
                function_name = f"{http_method.lower()}_{model_name}"
                summary = method_info.get('summary', '')
                description = f"{plugin_desc}{' | ' + summary if summary else ''}"

                # 抓 schema，依 method 判斷
                request_schema = {}
                if http_method.lower() in ['post', 'put', 'patch']:
                    schema = method_info.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
                    if schema:
                        request_schema = flatten_enum(schema)
                else:  # get / delete / head 等
                    request_schema = method_info.get('parameters', [])

                functions.append({
                    "function_name": function_name,
                    "description": description,
                    "schema": request_schema,
                    "method": http_method,
                    "path": path
                })
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        tools = []

        for api in functions:
            tool = types.Tool(
                name=api['function_name'],
                description=api['description'],
                inputSchema=api['schema'] if isinstance(api['schema'], dict) and api['schema'] else {
                    "type": "object",
                    "properties": {}
                }
            )
            tools.append(tool)
   
        return tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        動態處理 Tool，呼叫對應 API
        """
        print(f"handle_call_tool...{name}", file=sys.stderr)
        # 依 tool name 取得對應 API 設定
        api_info = next((f for f in functions if f["function_name"] == name), None)
        if not api_info:
            raise ValueError(f"Unknown tool: {name}")

        method = api_info['method'].lower()
        path = api_info['path']
        api_endpoint = f"https://superiorapis-creator.cteam.com.tw{path}"
        headers = {"token": TOKEN}
        print(f"API endpoint: {api_endpoint}")
        print(f"Headers: {headers}")
        print(f"Arguments: {arguments}")
        try:
            async with aiohttp.ClientSession() as session:
                if method == 'get':
                    async with session.get(api_endpoint, headers=headers, params=arguments or {}) as response:
                        result = await response.json()
                else:
                    async with getattr(session, method)(api_endpoint, headers=headers, json=arguments or {}) as response:
                        result = await response.json()

                if response.status == 200:
                    content = json.dumps(result, ensure_ascii=False)
                else:
                    content = json.dumps({"error": f"API failed with status code: {response.status}"}, ensure_ascii=False)

        except Exception as e:
            content = json.dumps({"error": f"API request error: {str(e)}"}, ensure_ascii=False)

        # 回傳訊息到前端
        return [
            types.TextContent(
                type="text",
                text=content
            )
        ]


async def main():
    print("Starting MCP server...")
    await register_tools()
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-superiorapis",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "mcp_superiorapis.server":
    import asyncio
    asyncio.run(main())