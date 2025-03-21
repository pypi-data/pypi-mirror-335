# mcp-browser-use: MCP server for browser-use

[![Version](https://img.shields.io/pypi/v/mcp-browser-use.svg)](https://pypi.org/project/mcp-browser-use/) [![Python Versions](https://img.shields.io/pypi/pyversions/mcp-browser-use.svg)](https://pypi.org/project/mcp-browser-use/) [![License](https://img.shields.io/pypi/l/mcp-browser-use.svg)](https://pypi.org/project/mcp-browser-use/)

**mcp-browser-use** is the easiest way to connect any MCP client (like Claude or Cursor) with the browser using [browser-use](https://github.com/browser-use/browser-use).

Unlike other `browser-use` MCPs that make you pay for an LLM API key, this one just uses the LLM that's already set up in your MCP client.

[📺 Demo](https://x.com/vortex_ape/status/1900953901588729864)

## Quickstart

You can start using `mcp-browser-use` with an MCP client by putting the following command in the relevant config:

```bash
uvx mcp-browser-use
```

**Note**: Provide the full path to uvx to prevent MCP client failing to start the server.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## Versioning

`mcp-browser-use` uses [Semantic Versioning](https://semver.org/). For the available versions, see the tags on the GitHub repository.

## License

This project is licensed under the Apache 2.0 License, see the [LICENSE](https://github.com/vinayak-mehta/mcp-browser-use/blob/master/LICENSE) file for details.
