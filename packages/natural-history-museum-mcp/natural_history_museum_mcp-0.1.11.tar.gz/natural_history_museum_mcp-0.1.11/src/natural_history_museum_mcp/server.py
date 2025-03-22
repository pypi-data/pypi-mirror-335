import sys
from typing import Literal

import json
import logging

from mcp import stdio_server

from natural_history_museum_mcp import nhm_api
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

COMMUNICATION_TYPE: Literal["stdio", "sse"] = "stdio" # For talking to clients locally

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    )
logger = logging.getLogger("NaturalHistoryMuseumMCPServer")

class SpecimenSearch(BaseModel):
    search_term: str

def search_specimens(query: str, limit: int) -> str:
    print("Starting search specimens", file=sys.stderr)
    nhm_api_result = nhm_api.get_by_query(query, limit)

    return json.dumps(nhm_api_result)

async def serve():
    server = Server("nhm-api")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="Le search",
                description="Search results from Natural History Museum",
                inputSchema=SpecimenSearch.SCHEMA,
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = search_specimens(name, arguments["limit"])
        return [TextContent(
            type="text",
            text=json.dumps(result),
        )]
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)