"""FastMCP server that groups the organization's pubmat tools."""

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from fastmcp.utilities.types import Image

from tempfile import TemporaryDirectory
from pathlib import Path

import httpx
from MCP_remove_background.tools.remove_background import (  # pyright: ignore[reportMissingTypeStubs]
    list_background_models as _list_background_models,
    remove_background as _remove_background,
)

mcp = FastMCP("ACM Pubmat Helper")




@mcp.tool()
async def remove_image_background(
    image_path: str,
    output_path: str | None = None,
    model: str = "u2net",
) -> dict[str, Any]:
    """
    Remove an image background and save a transparent PNG.

    The image path must be accessible to the machine running this MCP server.
    """
    result = await _remove_background(
        image_path=image_path,
        output_path=output_path,
        model=model,
        try_floodfill_first=False,
    )
    return result.model_dump()

@mcp.tool()
async def remove_image_background_from_url(
    image_url: str,
    model: str = "u2net",
) -> ToolResult:
    """
    Download an image from a URL,
    remove its background, and *return* the transparent PNG plus metadata.
    """

    ## Download the image from the URL

    # Step 1: get a response from the URL
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        # Check that `response.content` contains the image
        print(f"Received response of type {response.headers.get('content-type')}, "
              f"size {len(response.content)}")
    # Now we copy it to some temporary file for handling on this machine

    with TemporaryDirectory() as temp_dir_name:
        input_path = Path(temp_dir_name) / "input.jpg"
        input_path.write_bytes(response.content)

        ## Remove_image_background(...)
        metadata = await _remove_background(str(input_path))

        ## Package the image into the output
        assert metadata.output_path is not None
        output_path = Path(metadata.output_path)
        output_bytes = output_path.read_bytes() # ...now what?
        processed_image = Image(
            data = output_bytes,
            format = "png",
        )

        ## Return the image plus the metadata
        return ToolResult(
            content = [processed_image],
            structured_content = metadata.model_dump(),
        )




@mcp.tool()
def list_background_models() -> dict[str, Any]:
    """List the background-removal models available to this helper."""
    return _list_background_models().model_dump()


def main() -> None:
    """Run the helper over the default local stdio transport."""
    mcp.run()