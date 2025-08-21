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

from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult

from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig


async def get_dataset_info(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
    dataset_id: Optional[str] = None,
) -> ToolResult:
  """Gets information about a BigQuery dataset.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    bigquery_tool_config: The BigQuery tool config.
    dataset_id: The ID of the dataset to get information about. If not set, the
      default dataset ID from the config will be used.

  Returns:
    A ToolResult containing the dataset information.
  """
  if not dataset_id and bigquery_tool_config:
    dataset_id = bigquery_tool_config.default_dataset_id
  if not dataset_id:
    return ToolResult.from_error("Dataset ID must be provided or set in config.")

  try:
    dataset = client.get_dataset(dataset_id)
    info = {
        "dataset_id": dataset.dataset_id,
        "project_id": dataset.project,
        "location": dataset.location,
        "description": dataset.description,
        "labels": dataset.labels,
        "creation_time": dataset.created.isoformat(),
        "last_modified_time": dataset.modified.isoformat(),
        "default_table_expiration_ms": dataset.default_table_expiration_ms,
        "default_partition_expiration_ms": (
            dataset.default_partition_expiration_ms
        ),
    }
    return ToolResult.success(info)
  except Exception as e:
    return ToolResult.from_error(f"Error getting dataset info: {e}")


async def get_table_info(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
    dataset_id: Optional[str] = None,
    table_id: Optional[str] = None,
) -> ToolResult:
  """Gets information about a BigQuery table.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    bigquery_tool_config: The BigQuery tool config.
    dataset_id: The ID of the dataset containing the table. If not set, the
      default dataset ID from the config will be used.
    table_id: The ID of the table to get information about. If not set, the
      default table ID from the config will be used.

  Returns:
    A ToolResult containing the table information.
  """
  if not dataset_id and bigquery_tool_config:
    dataset_id = bigquery_tool_config.default_dataset_id
  if not table_id and bigquery_tool_config:
    table_id = bigquery_tool_config.default_table_id

  if not dataset_id or not table_id:
    return ToolResult.from_error(
        "Dataset ID and Table ID must be provided or set in config."
    )

  try:
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    info = {
        "table_id": table.table_id,
        "dataset_id": table.dataset_id,
        "project_id": table.project,
        "location": table.location,
        "description": table.description,
        "labels": table.labels,
        "creation_time": table.created.isoformat(),
        "last_modified_time": table.modified.isoformat(),
        "num_rows": table.num_rows,
        "num_bytes": table.num_bytes,
        "schema": [
            {"name": field.name, "field_type": field.field_type, "mode": field.mode}
            for field in table.schema
        ],
    }
    return ToolResult.success(info)
  except Exception as e:
    return ToolResult.from_error(f"Error getting table info: {e}")


async def list_dataset_ids(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
    project_id: Optional[str] = None,
) -> ToolResult:
  """Lists the IDs of all datasets in a project.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    bigquery_tool_config: The BigQuery tool config.
    project_id: The ID of the project to list datasets from. If not set, the
      project ID will be inferred from the environment.

  Returns:
    A ToolResult containing a list of dataset IDs.
  """
  try:
    datasets = list(client.list_datasets(project=project_id))
    dataset_ids = [dataset.dataset_id for dataset in datasets]
    return ToolResult.success({"dataset_ids": dataset_ids})
  except Exception as e:
    return ToolResult.from_error(f"Error listing dataset IDs: {e}")


async def list_table_ids(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
    dataset_id: Optional[str] = None,
) -> ToolResult:
  """Lists the IDs of all tables in a dataset.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    bigquery_tool_config: The BigQuery tool config.
    dataset_id: The ID of the dataset to list tables from. If not set, the
      default dataset ID from the config will be used.

  Returns:
    A ToolResult containing a list of table IDs.
  """
  if not dataset_id and bigquery_tool_config:
    dataset_id = bigquery_tool_config.default_dataset_id
  if not dataset_id:
    return ToolResult.from_error("Dataset ID must be provided or set in config.")

  try:
    tables = list(client.list_tables(dataset_id))
    table_ids = [table.table_id for table in tables]
    return ToolResult.success({"table_ids": table_ids})
  except Exception as e:
    return ToolResult.from_error(f"Error listing table IDs: {e}")


async def get_table_schema(
    client: bigquery.Client,
    readonly_context: ReadonlyContext,
    bigquery_tool_config: Optional[BigQueryToolConfig] = None,
    dataset_id: Optional[str] = None,
    table_id: Optional[str] = None,
) -> ToolResult:
  """Gets the schema of a BigQuery table.

  Args:
    client: The BigQuery client.
    readonly_context: The readonly context.
    bigquery_tool_config: The BigQuery tool config.
    dataset_id: The ID of the dataset containing the table. If not set, the
      default dataset ID from the config will be used.
    table_id: The ID of the table to get the schema for. If not set, the
      default table ID from the config will be used.

  Returns:
    A ToolResult containing the table schema.
  """
  if not dataset_id and bigquery_tool_config:
    dataset_id = bigquery_tool_config.default_dataset_id
  if not table_id and bigquery_tool_config:
    table_id = bigquery_tool_config.default_table_id

  if not dataset_id or not table_id:
    return ToolResult.from_error(
        "Dataset ID and Table ID must be provided or set in config."
    )

  try:
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    schema = [
        {"name": field.name, "field_type": field.field_type, "mode": field.mode}
        for field in table.schema
    ]
    return ToolResult.success({"schema": schema})
  except Exception as e:
    return ToolResult.from_error(f"Error getting table schema: {e}")