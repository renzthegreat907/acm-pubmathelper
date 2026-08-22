"""FastMCP server that groups the organization's pubmat tools."""

############################################################
############################################################
# Module imports

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from fastmcp.utilities.types import Image

from tempfile import TemporaryDirectory
from pathlib import Path

import httpx
from MCP_remove_background.tools.remove_background import (  # pyright: ignore[reportMissingTypeStubs]
    list_background_models as _list_background_removal_models,
    remove_background as _remove_background,
)

import pubmathelper.logger as logger # pyright: ignore[reportMissingTypeStubs]

mcp = FastMCP("ACM Pubmat Helper")

############################################################
############################################################
# Main functions

@mcp.tool()
async def remove_image_background(
    image_url: str,
    url_source: str | None = None,
    model: str = "u2netp",
) -> ToolResult:
    """
    Download an image from a URL, remove its background,
    and return the transparent PNG plus metadata.

    Inputs:
    - `image_url`, the URL of the image to download.
    - `url_source`, the source of the URL if known.
      If there is special handling for the source, it is executed.
      If unspecified, the URL is detected for a supported source.
      Otherwise, the image is treated as a generic source.
    - `model`: The background removal model used. By default, this is `u2netp`.

    Outputs: a `ToolResult` which contains both the photo and the process metadata.
    """

    logger.log_memory("remove_image_background: upon calling `remove_image_background`")

    # We redirect function flow to a source-dedicated function.
    # First, let's find out what the URL source is, in case it is unspecified.
    if url_source is None: url_source = detect_source(image_url)
        # For the sake of testing, we always say via ChatGPT that a Wikimedia URL comes from there.

    logger.log_misc("Received request to remove image background:")
    logger.log_misc(f"-> {image_url=}")
    logger.log_misc(f"-> {url_source=}")
    logger.log_misc(f"-> {model=}")

    # Next, we redirect function flow.
    match url_source:
        case "wikimedia":
            return await rib_handle_wikimedia(image_url, model)
        case "chatgpt":
            return await rib_handle_chatgpt(image_url, model)
        case _:
            return await rib_handle_generic(image_url, model)


async def rib_handle_wikimedia(
    image_url: str,
    model: str = "u2netp",
) -> ToolResult:
    headers = {
        "User-Agent": "ACM-PubmatHelper/1.0 (contact: rrsibal@up.edu.ph)",
            # Yeah yeah, my professional email is okay for now
        "Accept": "image/*",
    }

    logger.log_memory("rib_handle_wikimedia: upon calling `rib_handle_wikimedia`")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            image_url,
            headers = headers
        )
        logger.log_memory("rib_handle_wikimedia: after getting url response")
        response.raise_for_status()

        # Check that `response.content` contains the image
        logger.log_misc(f"Received response of type {response.headers.get('content-type')}, "
                f"size {len(response.content)}")

    with TemporaryDirectory() as temp_dir_name:
        input_path = Path(temp_dir_name) / "input.jpg"
        input_path.write_bytes(response.content)
        logger.log_memory("rib_handle_wikimedia: after writing to temp `image_path`")

        ## Remove_image_background(...)
        metadata = await _remove_background(str(input_path), model = model)
        logger.log_memory("rib_handle_wikimedia: after invoking background remover")

        ## Package the image into the output
        assert metadata.output_path is not None
        output_path = Path(metadata.output_path)
        output_bytes = output_path.read_bytes() # ...now what?
        processed_image = Image(
            data = output_bytes,
            format = "png",
        )
        logger.log_memory("rib_handle_wikimedia: after processing the image")

        ## Return the image plus the metadata
        return ToolResult(
            content = [processed_image],
            structured_content = metadata.model_dump(),
        )

async def rib_handle_chatgpt(
    image_url: str,
    model: str = "u2netp",
) -> ToolResult:
    raise NotImplementedError("Not yet supported")

async def rib_handle_generic(
    image_url: str,
    model: str = "u2netp",
) -> ToolResult:
    raise NotImplementedError("Not yet supported")

@mcp.tool()
def list_background_removal_models() -> dict[str, Any]:
    """
    List the background-removal models available to this helper.
    
    Inputs: (none)

    Outputs: a `dict[str, Any]` which lists the background removal models.
    """
    return _list_background_removal_models().model_dump()

@mcp.tool()
def greet() -> ToolResult:
    """
    Greets the MCP Server, which greets you back with a message.
    Use this function to boot up the Render server,
    as well as to check for server responsiveness.

    Inputs: (none)

    Outputs: `str` (a message)
    """
    return ToolResult(content = ["Hello, from the ACM Pubmat Helper!"])

############################################################
############################################################
# Private functions, miscellaneous

def detect_source(url: str) -> str | None:
    """
    Attempts to detect the source of a URL.
    If the source is supported by background removal functions,
    returns the name of that source. Otherwise, returns `None`.
    """
    return None

async def remove_image_background_local(
    image_path: str,
    output_path: str | None = None,
    model: str = "u2netp",
) -> dict[str, Any]:
    """
    Remove an image background and save a transparent PNG.
    Used to generate examples of expected output for local testing.
    """
    result = await _remove_background(
        image_path=image_path,
        output_path=output_path,
        model=model,
        try_floodfill_first=False,
    )
    return result.model_dump()

def main() -> None:
    """Run the helper over the default local stdio transport."""
    mcp.run()
    logger.log_memory("startup")