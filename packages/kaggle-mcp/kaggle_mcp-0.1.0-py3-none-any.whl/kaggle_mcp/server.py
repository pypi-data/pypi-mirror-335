from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from pathlib import Path
import os

from .utils import (
    download_dataset,
    extract,
    get_logger,
)

server = Server("kaggle-mcp")
logger = get_logger(__name__)


@server.call_tool()
async def prepare_kaggle_dataset(
    name: str,
    arguments: dict,
) -> list[types.TextContent | types.EmbeddedResource]:
    """Download and extract a Kaggle dataset.
    
    Args:
        competition_id: The name of the Kaggle competition to download the dataset from.
    """
    if name != "prepare_kaggle_dataset":
        raise ValueError(f"Unknown tool: {name}")
    if "competition_id" not in arguments:
        raise ValueError("Missing required argument 'competition_id'")
    
    data_dir = Path(__file__).parent / "data" / arguments["competition_id"]
    os.makedirs(data_dir, exist_ok=True)
    zipfile = download_dataset(arguments["competition_id"], data_dir)
    extract(zipfile, data_dir)
    return [types.TextContent(
        type="text",
        text=f"Successfully Downloaded and Extracted dataset for {arguments['competition_id']}"
    )]

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="prepare_kaggle_dataset",
            description="Download and extract a Kaggle dataset.",
            inputSchema={
                "type": "object",
                "required": ["competition_id"],
                "properties": {
                    "competition_id": {
                        "type": "string",
                        "description": "The Name of the Kaggle competition to download the dataset from.",
                    }
                },
            },
        )
    ]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kaggle-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

