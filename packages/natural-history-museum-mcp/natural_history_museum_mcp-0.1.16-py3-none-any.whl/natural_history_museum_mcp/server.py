import json
import logging

from mcp import stdio_server

from natural_history_museum_mcp import nhm_api
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from natural_history_museum_mcp.constants import NhmTools


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    )
logger = logging.getLogger("NaturalHistoryMuseumMCPServer")

class SpecimenSearch(BaseModel):
    search_term: str

def search_specimens(search_term: str, limit: int=100) -> str:
    logger.info("Starting search specimens")
    nhm_api_result = nhm_api.get_by_query(search_term, limit)

    return json.dumps(nhm_api_result)

async def serve():
    server = Server("nhm-api")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=NhmTools.SPECIMEN_SEARCH,
                description="Search results from Natural History Museum",
                inputSchema=SpecimenSearch.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:

        match name:
            case NhmTools.SPECIMEN_SEARCH:
                result = search_specimens(arguments["search_term"], arguments["limit"])
                return [TextContent(
                    type="text",
                    text=json.dumps(result),
                )]
            case _:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}, please specify a tool from the provided tools list"
                )]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)