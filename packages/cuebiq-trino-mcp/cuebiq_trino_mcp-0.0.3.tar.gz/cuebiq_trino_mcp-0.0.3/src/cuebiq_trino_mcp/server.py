import sys
import argparse
import uvicorn

from loguru import logger
from mcp.server.fastmcp import FastMCP
from cuebiq_trino_mcp.config import ServerConfig, TrinoConfig
from typing import AsyncIterator, Dict, Any, List, Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dataclasses import dataclass
from cuebiq_trino_mcp.trino_client import TrinoClient
from cuebiq_trino_mcp.resources import register_trino_resources
from cuebiq_trino_mcp.tools import register_trino_tools
from cuebiq_trino_mcp.prompts import register_trino_prompts
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route



@dataclass
class AppContext:
    """Application context passed to all MCP handlers."""
    trino_client: TrinoClient
    config: ServerConfig
    is_healthy: bool = True


class ArgumentParser:
    """Handles parsing command-line arguments."""
    @staticmethod
    def parse_args() -> ServerConfig:
        parser = argparse.ArgumentParser(description="Cuebiq Trino MCP server")

        parser.add_argument("--name", default="Cuebiq Trino MCP", help="Server name")
        parser.add_argument("--version", default="0.0.1", help="Server version")
        parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport type")
        parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP server (SSE transport only)")
        parser.add_argument("--port", type=int, default=3000, help="Port for HTTP server (SSE transport only)")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        
        # Trino connection
        parser.add_argument("--trino-host", default="localhost", help="Trino host")
        parser.add_argument("--trino-port", type=int, default=8080, help="Trino port")
        parser.add_argument("--trino-user", default="cuebiq_ai", help="Trino user")
        parser.add_argument("--trino-password", help="Trino password")
        parser.add_argument("--trino-catalog", help="Default Trino catalog")
        parser.add_argument("--trino-schema", help="Default Trino schema")
        parser.add_argument("--trino-http-scheme", default="http", help="Trino HTTP scheme")

        args = parser.parse_args()
        
        return ServerConfig(
            name=args.name,
            version=args.version,
            transport_type=args.transport,
            host=args.host,
            port=args.port,
            debug=args.debug,
            trino=TrinoConfig(
                host=args.trino_host,
                port=args.trino_port,
                user=args.trino_user,
                password=args.trino_password,
                catalog=args.trino_catalog,
                schema=args.trino_schema,
                http_scheme=args.trino_http_scheme
            )
        )


class MCPApplication:
    """Handles the lifecycle of the MCP server."""
    def __init__(self):
        self.config = ArgumentParser.parse_args()
        self.trino_client = TrinoClient(self.config.trino)
        self.app_context = AppContext(trino_client=self.trino_client, config=self.config)
        self.mcp = FastMCP("Cuebiq Trino MCP", dependencies=["trino>=0.329.0"], lifespan=self.app_lifespan)

    @asynccontextmanager
    async def app_lifespan(self, mcp: FastMCP) -> AsyncIterator[AppContext]:
        logger.info("Initializing Cuebiq Trino MCP server")
        try:
            logger.info(f"Connecting to Trino at {self.config.trino.host}:{self.config.trino.port}")
            self.trino_client.connect()
            logger.info("Registering resources and tools")
            register_trino_resources(mcp, self.trino_client)
            register_trino_tools(mcp, self.trino_client)
            register_trino_prompts(mcp)
            logger.info("Trino Cuebiq MCP server initialized and ready")
            yield self.app_context
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            self.app_context.is_healthy = False
            yield self.app_context
        finally:
            logger.info("Shutting down Trino MCP server")
            if self.trino_client.conn:
                self.trino_client.disconnect()
            self.app_context.is_healthy = False

    def run(self):
        if self.config.transport_type == "stdio":
            logger.info("Starting Cuebiq Trino MCP server with STDIO transport")
            self.mcp.run()
        else:
            self._run_sse_server()

    def _run_sse_server(self):
        logger.info(f"Starting Cuebiq Trino MCP server with SSE transport on {self.config.host}:{self.config.port}")
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
        uvicorn.run(starlette_app, host= self.config.host, port=self.config.port)


def main():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    app = MCPApplication()
    app.run()


if __name__ == "__main__":
    main()