import asyncio
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




def register_tools():
    exec(f"""
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    \"\"\"
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    \"\"\"
    return [
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={{
                "type": "object",
                "properties": {{
                    "name": {{"type": "string"}},
                    "content": {{"type": "string"}},
                }},
                "required": ["name", "content"],
            }},
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    \"\"\"
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    \"\"\"
    
    if name != "add-note":
        raise ValueError(f"Unknown tool: {{name}}")

    if not arguments:
        raise ValueError("Missing arguments")

    note_name = arguments.get("name")
    content = arguments.get("content")

    if not note_name or not content:
        raise ValueError("Missing name or content")

    # Update server state
    notes[note_name] = content

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"Added note ' {{arguments}}",
        )
    ]
    """)

async def main():
    print("Starting MCP server...")

    register_tools()
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