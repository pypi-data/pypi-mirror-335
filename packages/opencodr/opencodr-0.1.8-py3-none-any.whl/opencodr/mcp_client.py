import asyncio
import logging
import os
import shutil
from typing import Any, Dict, List, Optional

from mcp import ClientSession, ServerCapabilities, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, Tool

from opencodr.config import MCPServerConfig


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: MCPServerConfig) -> None:
        self.name: str = name
        self.config = config
        self.stdio_context: Optional[Any] = None
        self.session: Optional[ClientSession] = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.capabilities: Optional[ServerCapabilities] = None

    async def initialize(self, sampling_callback=None) -> None:
        """Initialize the server connection."""
        command = (
            shutil.which("npx") if self.config.command == "npx" else self.config.command
        )

        if not command:
            raise ValueError("Command not found, and no fallback provided.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config.args,
            env=({**os.environ, **self.config.env} if self.config.env else None),
        )
        try:
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()
            self.session = ClientSession(
                read, write, sampling_callback=sampling_callback
            )
            await self.session.__aenter__()
            init_result = await self.session.initialize()
            self.capabilities = init_result.capabilities
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> List[Tool]:
        """List available tools from the server.

        Returns:
            A list of available tools.

        Raises:
            RuntimeError: If the server is not initialized.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.session.list_tools()

        supports_progress = (
            self.capabilities is not None
            and isinstance(self.capabilities.experimental, dict)
            and "progress" in self.capabilities.experimental
        )

        if supports_progress:
            logging.info(f"Server {self.name} supports progress tracking")

        return tools_response.tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> Optional[CallToolResult]:
        """Execute a tool with retry mechanism.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            retries: Number of retry attempts.
            delay: Delay between retries in seconds.

        Returns:
            Tool execution result.

        Raises:
            RuntimeError: If server is not initialized.
            Exception: If tool execution fails after all retries.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                supports_progress = (
                    self.capabilities is not None
                    and isinstance(self.capabilities.experimental, dict)
                    and "progress" in self.capabilities.experimental
                )

                if supports_progress:
                    logging.info(f"Executing {tool_name} with progress tracking...")
                    result = await self.session.call_tool(tool_name, arguments)
                else:
                    logging.info(f"Executing {tool_name}...")
                    result = await self.session.call_tool(tool_name, arguments)

                return result

            except Exception as e:
                attempt += 1
                logging.warning(
                    f"Error executing tool: {e}. Attempt {attempt} of {retries}."
                )
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise
        return None

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                if self.session:
                    try:
                        await self.session.__aexit__(None, None, None)
                    except Exception as e:
                        logging.warning(
                            f"Warning during session cleanup for {self.name}: {e}"
                        )
                    finally:
                        self.session = None

                if self.stdio_context:
                    try:
                        await self.stdio_context.__aexit__(None, None, None)
                    except (RuntimeError, asyncio.CancelledError) as e:
                        logging.info(
                            f"Note: Normal shutdown message for {self.name}: {e}"
                        )
                    except Exception as e:
                        logging.warning(
                            f"Warning during stdio cleanup for {self.name}: {e}"
                        )
                    finally:
                        self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")
