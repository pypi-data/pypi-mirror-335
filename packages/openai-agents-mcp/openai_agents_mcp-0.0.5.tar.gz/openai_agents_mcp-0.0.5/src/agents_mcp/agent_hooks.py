from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agents.lifecycle import AgentHooks
from agents.run_context import RunContextWrapper, TContext

from .server_registry import ensure_mcp_server_registry_in_context

if TYPE_CHECKING:
    from .agent import Agent


class MCPAgentHooks(AgentHooks[TContext]):
    """
    Agent hooks for MCP agents. This class acts as a passthrough for any existing hooks, while
    also loading MCP tools on agent start.
    """

    def __init__(self, agent: Agent, original_hooks: AgentHooks[TContext] | None = None) -> None:
        self.original_hooks = original_hooks
        self.agent = agent

    async def on_start(
        self, context_wrapper: RunContextWrapper[TContext], agent_instance: Any
    ) -> None:
        # First load MCP tools if needed
        if hasattr(self.agent, "mcp_servers") and self.agent.mcp_servers:
            # Ensure MCP server registry is in context
            ensure_mcp_server_registry_in_context(context_wrapper)

            # Load MCP tools
            await self.agent.load_mcp_tools(context_wrapper)

        # Then call the original hooks if they exist
        if self.original_hooks:
            await self.original_hooks.on_start(context_wrapper, agent_instance)

    async def on_tool_call(
        self, context_wrapper: RunContextWrapper[TContext], call: Any, index: int
    ) -> None:
        if self.original_hooks:
            await self.original_hooks.on_tool_call(context_wrapper, call, index)

    async def on_tool_result(
        self, context_wrapper: RunContextWrapper[TContext], result: Any, index: int
    ) -> None:
        if self.original_hooks:
            await self.original_hooks.on_tool_result(context_wrapper, result, index)

    async def on_model_response(
        self, context_wrapper: RunContextWrapper[TContext], response: Any
    ) -> None:
        if self.original_hooks:
            await self.original_hooks.on_model_response(context_wrapper, response)

    async def on_agent_response(
        self, context_wrapper: RunContextWrapper[TContext], response: Any
    ) -> None:
        if self.original_hooks:
            await self.original_hooks.on_agent_response(context_wrapper, response)

    async def on_agent_finish(
        self, context_wrapper: RunContextWrapper[TContext], output: Any
    ) -> None:
        if self.original_hooks:
            await self.original_hooks.on_agent_finish(context_wrapper, output)
