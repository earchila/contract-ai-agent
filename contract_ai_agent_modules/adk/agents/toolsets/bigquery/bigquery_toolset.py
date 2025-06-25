# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import List
from typing import Optional
from typing import Union

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from typing_extensions import override

from contract_ai_agent_modules.adk.agents.toolsets.bigquery import metadata_tool
from contract_ai_agent_modules.adk.agents.toolsets.bigquery import query_tool
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.base_toolset import BaseToolset
from contract_ai_agent_modules.adk.tools.base_toolset import ToolPredicate
from contract_ai_agent_modules.adk.utils.feature_decorator import experimental
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_tool import BigQueryTool
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig


@experimental
class BigQueryToolset(BaseToolset):
  """BigQuery Toolset contains tools for interacting with BigQuery data and metadata."""

  def __init__(
      self,
      *,
      tool_filter: Optional[Union[ToolPredicate, List[str]]] = None,
      credentials_config: Optional[BigQueryCredentialsConfig] = None,
      bigquery_tool_config: Optional[BigQueryToolConfig] = None,
      tool_name: Optional[str] = None,
  ):
    self.tool_filter = tool_filter
    self._credentials_config = credentials_config
    self._tool_config = bigquery_tool_config
    self.tool_name = tool_name

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
        BigQueryTool(
            func=func,
            credentials_config=self._credentials_config,
            bigquery_tool_config=self._tool_config,
        )
        for func in [
            metadata_tool.get_dataset_info,
            metadata_tool.get_table_info,
            metadata_tool.list_dataset_ids,
            metadata_tool.list_table_ids,
            query_tool.get_execute_sql(self._tool_config),
            metadata_tool.get_table_schema,
        ]
    ]

    if self.tool_name:
        return [
            tool
            for tool in all_tools
            if tool.name == self.tool_name
        ]
    else:
        return [
            tool
            for tool in all_tools
            if self._is_tool_selected(tool, readonly_context)
        ]

  @override
  async def close(self):
    pass