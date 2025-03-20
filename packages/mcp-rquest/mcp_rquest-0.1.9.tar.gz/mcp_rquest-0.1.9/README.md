# mcp-rquest

[![PyPI Version](https://img.shields.io/pypi/v/mcp-rquest.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/mcp-rquest/) [![Python Versions](https://img.shields.io/pypi/pyversions/mcp-rquest?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/mcp-rquest/) [![GitHub Stars](https://img.shields.io/github/stars/xxxbrian/mcp-rquest?style=flat-square&logo=github)](https://github.com/xxxbrian/mcp-rquest) [![License](https://img.shields.io/github/license/xxxbrian/mcp-rquest?style=flat-square)](https://github.com/xxxbrian/mcp-rquest)

A Model Context Protocol (MCP) server that provides advanced HTTP request capabilities for Claude and other LLMs. Built on [rquest](https://github.com/0x676e67/rquest), this server enables realistic browser emulation with accurate TLS/JA3/JA4 fingerprints, allowing models to interact with websites more naturally and bypass common anti-bot measures.

## Features

- **Complete HTTP Methods**: Support for GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, and TRACE
- **Browser Fingerprinting**: Accurate TLS, JA3/JA4, and HTTP/2 browser fingerprints
- **Content Handling**:
  - Automatic handling of large responses with token counting
  - HTML to Markdown conversion for better LLM processing
  - Secure storage of responses in system temporary directories
- **Authentication Support**: Basic, Bearer, and custom authentication methods
- **Request Customization**:
  - Headers, cookies, redirects
  - Form data, JSON payloads, multipart/form-data
  - Query parameters
- **SSL Security**: Uses BoringSSL for secure connections with realistic browser fingerprints

## Available Tools

- **HTTP Request Tools**:

  - `http_get` - Perform GET requests with optional parameters
  - `http_post` - Submit data via POST requests
  - `http_put` - Update resources with PUT requests
  - `http_delete` - Remove resources with DELETE requests
  - `http_patch` - Partially update resources
  - `http_head` - Retrieve only headers from a resource
  - `http_options` - Retrieve options for a resource
  - `http_trace` - Diagnostic request tracing

- **Response Handling Tools**:
  - `get_stored_response` - Retrieve stored large responses, optionally by line range
  - `get_stored_response_with_markdown` - Convert HTML responses to Markdown

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run _mcp-rquest_.

### Using pip

Alternatively you can install `mcp-rquest` via pip:

```bash
pip install mcp-rquest
```

After installation, you can run it as a script using:

```bash
python -m mcp_rquest
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

Using `uvx`:

```json
{
  "mcpServers": {
    "http-rquest": {
      "command": "uvx",
      "args": ["mcp-rquest"]
    }
  }
}
```

Using `pip`:

```json
{
  "mcpServers": {
    "http-rquest": {
      "command": "python",
      "args": ["-m", "mcp_rquest"]
    }
  }
}
```

Using `pipx`:

```json
{
  "mcpServers": {
    "http-rquest": {
      "command": "pipx",
      "args": ["run", "mcp-rquest"]
    }
  }
}
```

</details>

## Browser Emulation

mcp-rquest leverages rquest's powerful browser emulation capabilities to provide realistic browser fingerprints, which helps bypass bot detection and access content normally available only to standard browsers. Supported browser fingerprints include:

- Chrome (multiple versions)
- Firefox
- Safari (including iOS and iPad versions)
- Edge
- OkHttp

This ensures that requests sent through mcp-rquest appear as legitimate browser traffic rather than bot requests.

## Development

### Setting up a Development Environment

1. Clone the repository
2. Create a virtual environment using uv:
   ```bash
   uv venv
   ```
3. Activate the virtual environment:
   ```bash
   # Unix/macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Acknowledgements

- This project is built on top of [rquest](https://github.com/0x676e67/rquest), which provides the advanced HTTP client with browser fingerprinting capabilities.
- rquest is based on a fork of [reqwest](https://github.com/seanmonstar/reqwest).
