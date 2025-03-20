import json
import os
import tempfile
import uuid
from typing import Any, Dict

import anyio
import click
import mcp.types as types
import rnet
import tiktoken
from markdownify import markdownify as md
from mcp.server.lowlevel import Server
from rnet import HeaderMap

# Storage for responses - use system temp directory
RESPONSE_STORAGE_DIR = os.path.join(tempfile.gettempdir(), "mcp-rquest-responses")
os.makedirs(RESPONSE_STORAGE_DIR, exist_ok=True)
response_metadata = {}  # UUID to metadata mapping


def get_content_type(headers: HeaderMap) -> str:
    """
    Get the content type from the headers.
    """
    # Use header_map_to_dict to get the content type
    headers_dict = header_map_to_dict(headers)
    return headers_dict.get("content-type", "unknown")


def store_response(content: str, content_type: str = "unknown") -> Dict[str, Any]:
    """
    Store HTTP response content in a file and return metadata about the stored content.
    """

    response_id = str(uuid.uuid4())
    file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")

    # Store the content to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Calculate metadata
    lines = content.count("\n") + 1
    char_count = len(content)

    # Calculate token count using tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's cl100k_base encoding
    token_count = len(encoding.encode(content))

    # Store metadata
    metadata = {
        "id": response_id,
        "content_type": content_type,
        "size_bytes": len(content.encode("utf-8")),
        "char_count": char_count,
        "line_count": lines,
        "token_count": token_count,  # Add token count to metadata
        "preview": content[:50] + "..." if len(content) > 50 else content,
        "tips": " ".join([
            "Response content is large and may consume many tokens.",
            "Consider using get_stored_response_with_markdown to retrieve the full content in markdown format.",
        ])
        if "html" in content_type.lower()
        else " ".join([
            "Response content is large and may consume many tokens.",
            "Consider asking the user for permission before retrieving the full content.",
            "You can use get_stored_response with start_line and end_line parameters to retrieve only a portion of the content.",
        ]),
    }
    response_metadata[response_id] = metadata

    return metadata


def should_store_content(content: str, force_store: bool = False) -> bool:
    """
    Determine if content should be stored based on token count or force flag.
    Returns True if content token count > 500 tokens or force_store is True.
    Using tiktoken for accurate AI token estimation.
    """
    if force_store:
        return True

    # Use tiktoken to count tokens accurately
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding for newer models
        token_count = len(encoding.encode(content))
        return token_count > 500  # Threshold of 500 tokens (approx. 375-750 words)
    except Exception:
        # Fallback to character count if tiktoken fails
        return len(content) > 2000

def header_map_to_dict(headers: HeaderMap) -> dict:
    """
    Convert HeaderMap to a dictionary using items() iterator.
    """
    result = {}
    for key, value in headers.items():
        # Convert keys and values to strings
        str_key = key.decode('utf-8') if isinstance(key, bytes) else str(key)
        str_value = value.decode('utf-8') if isinstance(value, bytes) else value
        result[str_key] = str_value
    return result

def cookies_to_dict(cookies) -> dict:
    """
    Convert cookies to a serializable dictionary format.
    """
    if not cookies:
        return {}

    # Handle different cookie object types
    if hasattr(cookies, "items"):
        # If it's a dict-like object, convert it to a dict
        return dict(cookies.items())
    elif hasattr(cookies, "__iter__"):
        # If it's an iterable, convert to a dict using key/value pairs
        cookie_dict = {}
        for cookie in cookies:
            if hasattr(cookie, "key") and hasattr(cookie, "value"):
                cookie_dict[str(cookie.key)] = str(cookie.value)
            elif isinstance(cookie, tuple) and len(cookie) >= 2:
                cookie_dict[str(cookie[0])] = str(cookie[1])
        return cookie_dict
    else:
        # If we can't handle the cookie object, return an empty dict
        return {}

async def perform_http_request(
    method: str,
    url: str,
    proxy: str = None,
    headers: dict = None,
    cookies: dict = None,
    allow_redirects: bool = True,
    max_redirects: int = 10,
    auth: str = None,
    bearer_auth: str = None,
    basic_auth: tuple[str, str] = None,
    query: list[tuple[str, str]] = None,
    form: list[tuple[str, str]] = None,
    json_payload: dict = None,
    body: dict = None,
    multipart: list[tuple[str, str]] = None,
    force_store_response_content: bool = False,
) -> Dict[str, Any]:
    """
    Common implementation for HTTP requests.
    """

    # Handle authentication
    kwds = {}
    if proxy:
        kwds["proxy"] = proxy
    if headers:
        kwds["headers"] = headers
    if cookies:
        kwds["cookies"] = cookies
    if allow_redirects:
        kwds["allow_redirects"] = allow_redirects
    if max_redirects:
        kwds["max_redirects"] = max_redirects
    if auth:
        kwds["auth"] = auth
    if bearer_auth:
        kwds["bearer_auth"] = bearer_auth
    if basic_auth:
        # Convert basic_auth list to tuple if needed
        kwds["basic_auth"] = tuple(basic_auth)
    if query:
        # Convert list of lists to list of tuples if needed
        kwds["query"] = [tuple(q) for q in query]
    if form:
        # Convert list of lists to list of tuples if needed
        kwds["form"] = [tuple(f) for f in form]
    if json_payload:
        kwds["json"] = json_payload
    if body:
        kwds["body"] = body
    if multipart:
        # Convert list of lists to list of tuples if needed
        kwds["multipart"] = [tuple(m) for m in multipart]

    resp = await getattr(rnet.Client(), method.lower())(url, **kwds)

    if "application/json" in get_content_type(resp.headers):
        content = await resp.json()
    else:
        content = await resp.text()

    # Prepare response data
    response_data = {
        "status": resp.status,
        "status_code": str(resp.status_code),
        "headers": header_map_to_dict(resp.headers),
        "cookies": cookies_to_dict(resp.cookies),
        "url": resp.url,
    }

    # Store content if needed based on length or force flag
    if should_store_content(content, force_store_response_content):
        metadata = store_response(content, get_content_type(resp.headers))
        response_data["response_content"] = metadata
    else:
        response_data["content"] = content

    return [types.TextContent(type="text", text=json.dumps(response_data, ensure_ascii=False))]

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-rquest")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls"""

        if name == "http_get":
            return await perform_http_request("GET", **arguments)
        elif name == "http_post":
            return await perform_http_request("POST", **arguments)
        elif name == "http_put":
            return await perform_http_request("PUT", **arguments)
        elif name == "http_delete":
            return await perform_http_request("DELETE", **arguments)
        elif name == "http_patch":
            return await perform_http_request("PATCH", **arguments)
        elif name == "http_head":
            return await perform_http_request("HEAD", **arguments)
        elif name == "http_options":
            return await perform_http_request("OPTIONS", **arguments)
        elif name == "http_trace":
            return await perform_http_request("TRACE", **arguments)
        elif name == "get_stored_response":
            response_id = arguments.get("response_id")
            start_line = arguments.get("start_line")
            end_line = arguments.get("end_line")

            if response_id not in response_metadata:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Response with ID {response_id} not found"}))]

            metadata = response_metadata[response_id]
            file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if start_line is not None and end_line is not None:
                    # Convert to 0-based indexing
                    start_line = max(1, start_line) - 1
                    end_line = min(metadata["line_count"], end_line)

                    # Extract the specified lines
                    lines = content.splitlines()
                    if start_line < len(lines) and end_line >= start_line:
                        partial_content = "\n".join(lines[start_line:end_line])
                        result = {
                            **metadata,
                            "content": partial_content,
                            "is_partial": True,
                            "start_line": start_line + 1,
                            "end_line": end_line,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

                # Return full content
                result = {**metadata, "content": content, "is_partial": False}
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Failed to retrieve response: {str(e)}"}, ensure_ascii=False))]

        elif name == "get_stored_response_with_markdown":
            response_id = arguments.get("response_id")

            if response_id not in response_metadata:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Response with ID {response_id} not found"}))]

            metadata = response_metadata[response_id]
            file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")
            content_type = metadata["content_type"]

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Convert HTML to Markdown if applicable
                if "html" in content_type.lower():
                    try:
                        markdown_content = md(content)
                        result = {
                            **metadata,
                            "content": markdown_content,
                            "is_markdown": True,
                            "original_content_type": content_type,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                    except Exception as e:
                        result = {
                            "error": f"Failed to convert HTML to Markdown: {str(e)}",
                            "content": content,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                else:
                    # Non-HTML content should not use `get_stored_response_with_markdown`
                    return [types.TextContent(type="text", text=json.dumps({"error": "Non-HTML content should use `get_stored_response`"}))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Failed to retrieve response: {str(e)}"}, ensure_ascii=False))]
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="http_get",
                description="Make an HTTP GET request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_post",
                description="Make an HTTP POST request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_put",
                description="Make an HTTP PUT request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_delete",
                description="Make an HTTP DELETE request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_patch",
                description="Make an HTTP PATCH request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_head",
                description="Make an HTTP HEAD request to retrieve only headers from the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_options",
                description="Make an HTTP OPTIONS request to retrieve options for the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_trace",
                description="Make an HTTP TRACE request for diagnostic tracing of the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="get_stored_response",
                description="Retrieve a stored HTTP response by its ID",
                inputSchema={
                    "type": "object",
                    "required": ["response_id"],
                    "properties": {
                        "response_id": {"type": "string", "description": "ID of the stored response"},
                        "start_line": {"type": "integer", "description": "Starting line number (1-indexed)"},
                        "end_line": {"type": "integer", "description": "Ending line number (inclusive)"},
                    }
                }
            ),
            types.Tool(
                name="get_stored_response_with_markdown",
                description="Retrieve a stored HTTP response by its ID, converted to Markdown if HTML",
                inputSchema={
                    "type": "object",
                    "required": ["response_id"],
                    "properties": {
                        "response_id": {"type": "string", "description": "ID of the stored response"},
                    }
                }
            ),
        ]

    # Setup server based on transport type
    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0
