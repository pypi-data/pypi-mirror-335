# kaggle-mcp MCP server

A MCP server for Kaggle Apis

## Components

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

Ensure that you have downloaded your Kaggle credentials
(`kaggle.json`) and placed it in the `~/.kaggle/` directory (this is the default
location where the Kaggle API looks for your credentials)

Otherwise you can add the env `KAGGLE_USERNAME` and `KAGGLE_KEY` to the mcp config

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "kaggle-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/{username}/Work/kaggle-mcp",
        "run",
        "kaggle-mcp"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "kaggle-mcp": {
      "command": "uvx",
      "args": [
        "kaggle-mcp"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/{username}/Work/kaggle-mcp run kaggle-mcp
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.