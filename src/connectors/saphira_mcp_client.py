"""
Saphira MCP Client Module
=========================
Production-ready FastAPI + Model Context Protocol (MCP) Client integration
for Saphira AI. Dynamically discovers tools from any running MCP server
(GitHub, Supabase, local system tools, etc.), converts them into callable
functions, and registers them into Saphira's execution engine.

© 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
"""

import asyncio
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# MCP Python SDK Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ToolExecutionRequest(BaseModel):
    server_name: str = Field(..., description="Target registered MCP server name")
    tool_name: str = Field(..., description="Exact tool function name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")


class SaphiraMCPManager:
    """
    Orchestrates dynamic tool discovery and execution across multiple MCP servers
    for the Saphira AI ecosystem.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.tool_catalog: Dict[str, List[Dict[str, Any]]] = {}

    async def connect_server(
        self, server_name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Connects to an MCP server via Stdio transport, initializes session,
        and dynamically fetches available tools.
        """
        server_params = StdioServerParameters(command=command, args=args, env=env)

        # Establish Stdio transport stream
        read_stream, write_stream = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Initialize MCP Client Session
        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()

        self.sessions[server_name] = session

        # Discover tools dynamically
        tools_response = await session.list_tools()
        parsed_tools = []

        for tool in tools_response.tools:
            parsed_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
            )

        self.tool_catalog[server_name] = parsed_tools
        return parsed_tools

    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executes a dynamic MCP tool call on a connected server.
        """
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"MCP Server '{server_name}' is not connected.")

        result = await session.call_tool(tool_name, arguments=arguments)
        return result.content

    async def shutdown(self) -> None:
        """Cleanly releases all MCP transport connections."""
        await self.exit_stack.aclose()


# Initialize Global Saphira MCP Orchestrator
mcp_manager = SaphiraMCPManager()

# FastAPI Service Application
app = FastAPI(
    title="Saphira AI - Dynamic MCP Engine",
    version="1.0.0",
    description="Tool-use gateway connecting Saphira to external MCP servers.",
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Connect default system MCP servers upon Saphira system startup.
    Example: Initializing a local SQLite or File System MCP server.
    """
    try:
        # Example: Connecting a local filesystem MCP server
        await mcp_manager.connect_server(
            server_name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
        )
    except Exception as err:
        print(f"[Saphira MCP] Warning - Server auto-connect deferred: {err}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await mcp_manager.shutdown()


@app.get("/v1/mcp/tools", summary="List all dynamically loaded tools")
async def list_tools() -> Dict[str, Any]:
    """Returns the aggregated catalog of all loaded tools across connected MCP servers."""
    return {"status": "success", "catalog": mcp_manager.tool_catalog}


@app.post("/v1/mcp/execute", summary="Dispatch dynamic tool call")
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
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as sys_err:
        raise HTTPException(status_code=500, detail=f"Tool Execution Error: {str(sys_err)}")
