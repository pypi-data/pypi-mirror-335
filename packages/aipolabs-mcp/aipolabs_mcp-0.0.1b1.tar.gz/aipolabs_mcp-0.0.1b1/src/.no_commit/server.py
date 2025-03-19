import asyncio
import anyio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
import mcp.server.websocket

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("aipolabs-mcp")



# async def fetch_website(
#     url: str,
# ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
#     headers = {
#         "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
#     }
#     async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
#         response = await client.get(url)
#         response.raise_for_status()
#         return [types.TextContent(type="text", text=response.text)]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """

    # send http request with httpx to api.aci.dev with api key:
    """
    curl -X 'GET' \
  'https://api.aci.dev/v1/apps?limit=100&offset=0' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 8c93a667306a9d4a7194c2ffc1dde810db3f9c89ac2aac26f4fca64bcdbc806a'
    """
    import httpx
    import json

    url = "https://api.aci.dev/v1/functions/search?format=anthropic&limit=5&offset=0"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "8c93a667306a9d4a7194c2ffc1dde810db3f9c89ac2aac26f4fca64bcdbc806a"
    }
    response = httpx.get(url, headers=headers)

    functions = response.json()
    return [
        types.Tool(
            name=function["name"],
            description=function["description"],
            inputSchema=function["input_schema"],
        )
        for function in functions
    ]

    return [
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    # return [
    #     types.TextContent(
    #         type="text",
    #         text=f"result of handle_call_tool",
    #     )
    # ]
    print(f"Calling tool: {name} with arguments: {arguments}")
    if name != "add-note":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    note_name = arguments.get("name")
    content = arguments.get("content")

    if not note_name or not content:
        raise ValueError("Missing name or content")

    # Update server state
    notes[note_name] = content

    # Notify clients that resources have changed
    # await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"Added note '{note_name}' with content: {content}",
        )
    ]

# async def main():
#     # Run the server using stdin/stdout streams
#     async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
#         await server.run(
#             read_stream,
#             write_stream,
#             InitializationOptions(
#                 server_name="aipolabs-mcp",
#                 server_version="0.1.0",
#                 capabilities=server.get_capabilities(
#                     notification_options=NotificationOptions(),
#                     experimental_capabilities={},
#                 ),
#             ),
#         )

def main():
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    import uvicorn
    import time

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


    uvicorn.run(starlette_app, host="0.0.0.0", port=8888)
    time.sleep(3)

if __name__ == "__main__":
    # print("Starting MCP server...")
    # anyio.run(main)
    main()
    # print("MCP server started")