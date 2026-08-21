import asyncio

from pubmat_helper.server import mcp  # pyright: ignore[reportMissingTypeStubs]


def test_server_registers_pubmat_tools() -> None:
    tools = asyncio.run(mcp.get_tools())
    tool_names = set(tools)

    assert tool_names == {
        "greet",
        "list_background_removal_models",
        "remove_image_background",
    }