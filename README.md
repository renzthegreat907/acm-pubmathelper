# ACM Pubmat Helper

This project is an MCP gateway for organization-specific pubmat tools.
It currently delegates background removal to the separate
`MCP-remove-background` project.

## The architecture

```text
MCP client (later: ChatGPT)
              |
              v
       ACM Pubmat Helper
              |
              v
       MCP-remove-background
```

The helper is the public collection of tools. Each `@mcp.tool()` function is
an operation an MCP client can discover and call. The helper should contain
organization-specific decisions and workflow rules; specialized packages can
contain reusable image-processing implementation.

## Local setup

```bash
cd ~/dev/projects/acm_pubmathelper
poetry install
poetry run pytest
```

Run the helper over local stdio:

```bash
poetry run pubmat-helper
```

The current image tool accepts a path on the machine running the server. That
is convenient for local testing. A future remote ChatGPT version will need an
upload/download design because ChatGPT cannot directly provide a path on your
computer to Render.

## FastMCP mindset

An MCP server is a catalog of narrow tools, not one giant chatbot function.
Give each tool a clear name, a useful docstring, typed parameters, and a
structured return value. Keep tool registration in the server layer and put
processing logic in services or dependencies so each part can be tested alone.