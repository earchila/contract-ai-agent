from __future__ import annotations

from typing import List, Optional, Union
from typing_extensions import override

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.base_toolset import BaseToolset, ToolPredicate
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult
from contract_ai_agent_modules.adk.utils.feature_decorator import experimental


@experimental
class GeneralInsightsTool(BaseTool):
    """A tool for providing general insights about contracts."""

    def __init__(self, func):
        super().__init__(func)
        self._func = func

    async def _call(self, readonly_context: ReadonlyContext, **kwargs) -> ToolResult:
        return await self._func(readonly_context, **kwargs)


async def get_general_insights(readonly_context: ReadonlyContext, query: str) -> ToolResult:
    """Provides general insights or answers to questions about contracts.

    Args:
        query: The natural language query from the user.

    Returns:
        A ToolResult containing the general insight.
    """
    # Placeholder for actual general insights logic.
    # This would typically involve more advanced NLP and data retrieval.
    return ToolResult.success({"response": f"I am a General Insights tool. For your query: '{query}', I would provide a comprehensive answer based on available contract data."})


@experimental
class GeneralInsightsToolset(BaseToolset):
    """General Insights Toolset contains tools for providing general insights."""

    def __init__(
        self,
        *,
        tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
    ):
        self.tool_filter = tool_filter

    def _is_tool_selected(
        self, tool: BaseTool, readonly_context: ReadonlyContext
    ) -> bool:
        if self.tool_filter is None:
            return True

        if isinstance(self.tool_filter, ToolPredicate):
            return self.tool_filter(tool, readonly_context)

        if isinstance(self.tool_filter, list):
            return tool.name in self.tool_filter

        return False

    @override
    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        """Get tools from the toolset."""
        all_tools = [
            GeneralInsightsTool(func=get_general_insights),
        ]

        return [
            tool
            for tool in all_tools
            if self._is_tool_selected(tool, readonly_context)
        ]

    @override
    async def close(self):
        pass