from asyncio import run
from importlib.metadata import version as pkg_ver
from logging import getLogger
from traceback import format_exc

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData, TextContent, Tool
from pydantic import ValidationError

from scrapling_fetch_mcp._fetcher import fetch_page, fetch_pattern
from scrapling_fetch_mcp.tools import (
    PageFetchRequest,
    PatternFetchRequest,
    s_fetch_page_tool,
    s_fetch_pattern_tool,
)


async def serve() -> None:
    server: Server = Server("scrapling-fetch-mcp", pkg_ver("scrapling-fetch-mcp"))

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [s_fetch_page_tool, s_fetch_pattern_tool]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            if name == "s-fetch-page":
                request = PageFetchRequest(**arguments)
                result = await fetch_page(request)
                metadata_json = result.metadata.model_dump_json()
                content_with_metadata = f"METADATA: {metadata_json}\n\n{result.content}"
                return [TextContent(type="text", text=content_with_metadata)]
            elif name == "s-fetch-pattern":
                request = PatternFetchRequest(**arguments)
                result = await fetch_pattern(request)
                metadata_json = result.metadata.model_dump_json()
                content_with_metadata = f"METADATA: {metadata_json}\n\n{result.content}"
                return [TextContent(type="text", text=content_with_metadata)]
            else:
                raise McpError(
                    ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}")
                )
        except ValidationError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
        except Exception as e:
            logger = getLogger("scrapling_fetch_mcp")
            logger.error("DETAILED ERROR IN %s: %s", name, str(e))
            logger.error("TRACEBACK: %s", format_exc())
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR, message=f"Error processing {name}: {str(e)}"
                )
            )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
            raise_exceptions=True,
        )


def run_server():
    run(serve())


if __name__ == "__main__":
    run_server()
