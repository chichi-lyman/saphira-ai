"""
Saphira MCP Client Module
=========================
Production-ready Model Context Protocol (MCP) Client integration for Saphira AI.
Dynamically discovers tools from any running MCP server (GitHub, filesystem,
Supabase, local system tools, etc.) and exposes them via a FastAPI router
that mounts cleanly into the main Saphira application.

© 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
"""

from __future__ import annotations

import logging
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# MCP Python SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("saphira.mcp")

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolExecutionRequest(BaseModel):
    server_name: str = Field(..., description="Target registered MCP server name")
    tool_name: str = Field(..., description="Exact tool function name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")


class ConnectServerRequest(BaseModel):
    server_name: str = Field(..., description="Logical name for this MCP server")
    command: str = Field(..., description="Executable that launches the MCP server")
    args: List[str] = Field(default_factory=list, description="CLI arguments")
    env: Optional[Dict[str, str]] = Field(default=None, description="Optional environment overrides")


class SaphiraMCPManager:
    """
    Orchestrates dynamic tool discovery and execution across multiple MCP servers
    for the Saphira AI ecosystem (NovaAethrea / Agent Zero layer).
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.tool_catalog: Dict[str, List[Dict[str, Any]]] = {}
        self._started = False

    async def connect_server(
        self,
        server_name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Connects to an MCP server via Stdio transport, initializes the session,
        and dynamically fetches available tools.
        """
        if server_name in self.sessions:
            logger.info("MCP server '%s' already connected – returning cached catalog", server_name)
            return self.tool_catalog.get(server_name, [])

        server_params = StdioServerParameters(command=command, args=args, env=env)

        try:
            read_stream, write_stream = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()

            self.sessions[server_name] = session

            tools_response = await session.list_tools()
            parsed_tools: List[Dict[str, Any]] = []

            for tool in tools_response.tools:
                parsed_tools.append(
                    {
                        "name": tool.name,
                        "description": getattr(tool, "description", "") or "",
                        "input_schema": getattr(tool, "inputSchema", {}) or {},
                    }
                )

            self.tool_catalog[server_name] = parsed_tools
            logger.info(
                "Connected MCP server '%s' – discovered %d tools",
                server_name,
                len(parsed_tools),
            )
            return parsed_tools

        except Exception as exc:
            logger.exception("Failed to connect MCP server '%s': %s", server_name, exc)
            self.sessions.pop(server_name, None)
            self.tool_catalog.pop(server_name, None)
            raise

    async def execute_tool(
        self, server_name: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Executes a dynamic MCP tool call on a connected server."""
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"MCP Server '{server_name}' is not connected.")

        result = await session.call_tool(tool_name, arguments=arguments or {})
        return result.content

    async def shutdown(self) -> None:
        """Cleanly releases all MCP transport connections."""
        try:
            await self.exit_stack.aclose()
        finally:
            self.sessions.clear()
            self.tool_catalog.clear()
            self._started = False
            logger.info("SaphiraMCPManager shut down")

    async def bootstrap_default_servers(self) -> None:
        """
        Optionally connect well-known MCP servers based on environment variables.
        Safe to call multiple times; skips already-connected servers.
        """
        if self._started:
            return
        self._started = True

        # Filesystem MCP (optional)
        fs_root = os.getenv("MCP_FILESYSTEM_ROOT")
        if fs_root:
            try:
                await self.connect_server(
                    server_name="filesystem",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", fs_root],
                )
            except Exception as err:
                logger.warning("[Saphira MCP] filesystem auto-connect deferred: %s", err)

        # GitHub MCP (optional – requires token)
        gh_token = os.getenv("MCP_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
        if gh_token:
            try:
                await self.connect_server(
                    server_name="github",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_PERSONAL_ACCESS_TOKEN": gh_token},
                )
            except Exception as err:
                logger.warning("[Saphira MCP] github auto-connect deferred: %s", err)


# Global orchestrator instance used by the router and external agents
mcp_manager = SaphiraMCPManager()


@router.get("/tools", summary="List all dynamically loaded tools")
async def list_tools() -> Dict[str, Any]:
    """Returns the aggregated catalog of all loaded tools across connected MCP servers."""
    return {"status": "success", "catalog": mcp_manager.tool_catalog}


@router.post("/execute", summary="Dispatch dynamic tool call")
async def execute_mcp_tool(payload: ToolExecutionRequest) -> Dict[str, Any]:
    """Routes execution requests directly to the target MCP server."""
    try:
        output = await mcp_manager.execute_tool(
            server_name=payload.server_name,
            tool_name=payload.tool_name,
            arguments=payload.arguments,
        )
        return {
            "status": "success",
            "server": payload.server_name,
            "tool": payload.tool_name,
            "result": output,
        }
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err)) from val_err
    except Exception as sys_err:
        raise HTTPException(
            status_code=500, detail=f"Tool Execution Error: {sys_err}"
        ) from sys_err


@router.post("/connect", summary="Connect a new MCP server at runtime")
async def connect_mcp_server(payload: ConnectServerRequest) -> Dict[str, Any]:
    """Register and connect an additional MCP server, returning its tool list."""
    try:
        tools = await mcp_manager.connect_server(
            server_name=payload.server_name,
            command=payload.command,
            args=payload.args,
            env=payload.env,
        )
        return {"status": "success", "server": payload.server_name, "tools": tools}
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Unable to connect MCP server: {exc}"
        ) from exc
