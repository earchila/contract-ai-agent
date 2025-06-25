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
from typing import Any, Callable, Dict, List, Optional

from google.cloud import bigquery

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult

from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig


def get_execute_sql(
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
) -> Callable[..., Any]:
  """Returns a function that executes a BigQuery SQL query.

  Args:
    bigquery_tool_config: The BigQuery tool config.

  Returns:
    A function that executes a BigQuery SQL query.
  """

  @functools.wraps(execute_sql)
  async def execute_sql_with_config(
      client: bigquery.Client,
      readonly_context: ReadonlyContext,
      query: str,
      bigquery_tool_config: Optional[BigQueryToolConfig] = bigquery_tool_config,
  ) -> ToolResult:
    return await execute_sql(
        client, readonly_context, query, bigquery_tool_config
    )

  return execute_sql_with_config


async def execute_sql(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    query: str,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
) -> ToolResult:
  """Executes a BigQuery SQL query.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    query: The SQL query to execute.
    bigquery_tool_config: The BigQuery tool config.

  Returns:
    A ToolResult containing the query results.
  """
  if bigquery_tool_config and bigquery_tool_config.default_dataset_id:
      import re
      # Add the dataset prefix to all tables in the query
      query = re.sub(
          r"FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?",
          rf"FROM `{bigquery_tool_config.default_dataset_id}.\g<1>`",
          query,
      )
      query = re.sub(
          r"JOIN\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?",
          rf"JOIN `{bigquery_tool_config.default_dataset_id}.\g<1>`",
          query,
      )
  try:
    query_job = client.query(query)
    rows = query_job.result()

    results: List[Dict[str, Any]] = []
    max_rows = (
        bigquery_tool_config.max_rows if bigquery_tool_config else None
    )
    for i, row in enumerate(rows):
      if max_rows and i >= max_rows:
        break
      results.append(dict(row))

    return ToolResult.success({"results": results})
  except Exception as e:
    return ToolResult.from_error(f"Error executing SQL query: {e}")