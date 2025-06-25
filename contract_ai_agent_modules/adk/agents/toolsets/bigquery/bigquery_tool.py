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

import functools
from typing import Any, Callable, Optional

from google.cloud import bigquery
from google.cloud.bigquery import dbapi
from google.cloud.bigquery import query
from google.api_core import exceptions as api_exceptions # Import for general API exceptions

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult
from contract_ai_agent_modules.adk.utils.feature_decorator import experimental

from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig


@experimental
class BigQueryTool(BaseTool):
  """BigQuery tool for interacting with BigQuery data and metadata."""

  def __init__(
      self,
      func: Callable[..., Any],
      credentials_config: Optional[BigQueryCredentialsConfig] = None,
      bigquery_tool_config: Optional[BigQueryToolConfig] = None,
  ):
    super().__init__(func)
    self._credentials_config = credentials_config
    self._tool_config = bigquery_tool_config

  async def _call(
      self, readonly_context: ReadonlyContext, **kwargs
  ) -> ToolResult:
    """Calls the BigQuery tool.

    Args:
      readonly_context: The readonly context.
      **kwargs: The keyword arguments to pass to the tool.

    Returns:
      The tool result.
    """
    project_id = (
        self._credentials_config.project_id
        if self._credentials_config
        else None
    )
    location = (
        self._credentials_config.location if self._credentials_config else None
    )
    client = bigquery.Client(project=project_id, location=location)
    try:
      return await self._call_with_client(client, readonly_context, **kwargs)
    except Exception as e:
      print(f"Caught exception in BigQueryTool: {e}")
      return ToolResult.from_error(f"An unexpected error occurred in BigQueryTool: {e}")

  async def _call_with_client(
      self,
      client: bigquery.Client,
      readonly_context: ReadonlyContext,
      **kwargs,
  ) -> ToolResult:
    """Calls the BigQuery tool with a BigQuery client.

    Args:
      client: The BigQuery client.
      readonly_context: The readonly context.
      **kwargs: The keyword arguments to pass to the tool.

    Returns:
      The tool result.
    """
    return await self._func( # Change self.func to self._func
        client=client,
        readonly_context=readonly_context,
        bigquery_tool_config=self._tool_config,
        **kwargs,
    )