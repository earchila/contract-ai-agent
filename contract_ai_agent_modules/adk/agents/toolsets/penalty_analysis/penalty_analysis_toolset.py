from __future__ import annotations

from typing import List, Optional, Union
from typing_extensions import override

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.base_toolset import BaseToolset, ToolPredicate
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult
from contract_ai_agent_modules.adk.utils.feature_decorator import experimental


@experimental
class PenaltyAnalysisTool(BaseTool):
    """A tool for analyzing contract penalties."""

    def __init__(self, func):
        super().__init__(func)
        self._func = func

    async def _call(self, readonly_context: ReadonlyContext, **kwargs) -> ToolResult:
        return await self._func(readonly_context, **kwargs)


async def analyze_penalty(readonly_context: ReadonlyContext, query: str) -> ToolResult:
    """Analyzes contract penalties based on the query.

    Args:
        query: The natural language query from the user.

    Returns:
        A ToolResult containing the penalty analysis.
    """
    # Placeholder for actual penalty analysis logic.
    return ToolResult.success({"response": f"I am a Penalty Analysis tool. For your query: '{query}', I would analyze potential contract penalties."})


@experimental
class PenaltyAnalysisToolset(BaseToolset):
    """Penalty Analysis Toolset contains tools for analyzing contract penalties."""

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
            PenaltyAnalysisTool(func=analyze_penalty),
        ]

        return [
            tool
            for tool in all_tools
            if self._is_tool_selected(tool, readonly_context)
        ]

    @override
    async def close(self):
        pass