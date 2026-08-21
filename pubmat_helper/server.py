"""FastMCP server that groups the organization's pubmat tools."""

from typing import Any

from fastmcp import FastMCP

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
    """Remove an image background and save a transparent PNG.

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
def list_background_models() -> dict[str, Any]:
    """List the background-removal models available to this helper."""
    return _list_background_models().model_dump()


def main() -> None:
    """Run the helper over the default local stdio transport."""
    mcp.run()