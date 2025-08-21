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

from typing import List, Optional

import vertexai
from vertexai.generative_models import GenerativeModel, Tool
import os # Import os for environment variables
import subprocess

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.base_toolset import BaseToolset
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult
from contract_ai_agent_modules.adk.utils.feature_decorator import experimental

from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_toolset import BigQueryToolset
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.general_insights.general_insights_toolset import GeneralInsightsToolset
from contract_ai_agent_modules.adk.agents.toolsets.document_processing.document_processing_toolset import DocumentProcessingToolset


@experimental
class ContractAgent:
  """Main agent for contract management."""

  def __init__(
      self,
      bigquery_credentials_config: Optional[BigQueryCredentialsConfig] = None,
      bigquery_tool_config: Optional[BigQueryToolConfig] = None,
      model_name: str = "gemini-2.5-flash", # Default model name
  ):
    self._bigquery_toolset = BigQueryToolset(
        credentials_config=bigquery_credentials_config,
        bigquery_tool_config=bigquery_tool_config,
        tool_name="execute_sql",
    )
    self._general_insights_toolset = GeneralInsightsToolset()
    self._document_processing_toolset = DocumentProcessingToolset()

    # Initialize Vertex AI
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location=os.environ.get("GOOGLE_CLOUD_LOCATION"))
    # Get the model
    self._model = GenerativeModel(model_name)

  async def process_query(self, query: str) -> ToolResult:
    """Processes a natural language query related to contracts.

    Args:
      query: The natural language query from the user.

    Returns:
      A ToolResult containing the response from the relevant tool.
    """
    readonly_context = ReadonlyContext()
    schema_toolset = BigQueryToolset(
        credentials_config=self._bigquery_toolset._credentials_config,
        bigquery_tool_config=self._bigquery_toolset._tool_config,
        tool_name="get_table_schema",
    )
    schema_tools = await schema_toolset.get_tools(readonly_context)
    schema_tool = schema_tools[0]
    schema_result = await schema_tool._call(
        readonly_context, table_id="contracts"
    )
    if not schema_result.is_successful:
        return schema_result
    schema = schema_result.result["schema"]

    all_tools = await self._bigquery_toolset.get_tools(readonly_context)
    
    # Convert BaseTool objects to vertexai.generative_models.Tool objects
    vertexai_tools = [Tool(function_declarations=[tool.to_function_declaration()]) for tool in all_tools]

    # Send the query to the model
    chat_session = self._model.start_chat()
    prompt = f"""You are a BigQuery expert and a helpful assistant. Your primary goal is to provide accurate answers about contracts.

**Instructions:**
1.  **If the user asks for data (e.g., "list all contracts"), generate a SQL query.**
2.  **If the user asks to "explain the schema", you MUST return a JSON object with a single key, "schema_explanation", containing a list of objects. Each object must have "name", "type", and "description" keys.**
    **Example JSON Output:**
    ```json
    {{
      "schema_explanation": [
        {{
          "name": "contract_id",
          "type": "STRING",
          "description": "Unique identifier for the contract."
        }},
        {{
          "name": "contract_name",
          "type": "STRING",
          "description": "Name of the contract."
        }}
      ]
    }}
    ```
3.  **For any other general question (e.g., "what can you do?"), provide a clear, user-friendly response in standard text.**

**Schema for `contracts` table:**
{schema}

**SQL Generation Rules:**
- When a query requires the status of a contract, derive it using a `CASE` statement with the following logic:
  - **Active**: `CURRENT_DATE() BETWEEN start_date AND end_date`
  - **Expired**: `CURRENT_DATE() > end_date`
  - **Pending**: `CURRENT_DATE() < start_date`
- For upcoming expirations, consider contracts expiring in the next 90 days.
- For total penalty amount, sum the `penalty_amount` column.
- For average contract value, calculate the average of the `price` column.

**User Request:**
{query}
"""
    response = chat_session.send_message(prompt, tools=vertexai_tools)

    # Process the model's response
    if response.candidates:
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.function_call:
                    # Execute the tool call
                    tool_call = part.function_call
                    tool_name = tool_call.name
                    tool_args = {k: v for k, v in tool_call.args.items()}

                    # Find the tool and execute it
                    for tool in all_tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = await tool._call(readonly_context, **tool_args)
                                if tool_result.is_successful:
                                    return tool_result
                                else:
                                    return ToolResult.from_error(f"Tool execution failed: {tool_result.error}")
                            except Exception as e:
                                return ToolResult.from_error(f"Error executing tool '{tool_name}': {e}")
                    return ToolResult.from_error(f"Tool '{tool_name}' not found.")
                elif part.text:
                    # If the model returns text, check if it's a valid SQL query
                    sql_query = part.text.strip()
                    # A simple check to see if the response is likely a SQL query
                    if sql_query.upper().startswith('SELECT') or '```sql' in sql_query:
                        # Extract SQL from markdown code block if present
                        if '```sql' in sql_query:
                            sql_query = sql_query.split('```sql')[1].split('```')[0].strip()
                        
                        # Find the execute_sql tool and execute it
                        for tool in all_tools:
                            if tool.name == "execute_sql":
                                try:
                                    tool_result = await tool._call(readonly_context, query=sql_query)
                                    if tool_result.is_successful:
                                        return tool_result
                                    else:
                                        return ToolResult.from_error(f"SQL execution failed: {tool_result.error}")
                                except Exception as e:
                                    return ToolResult.from_error(f"Error executing SQL query: {e}")
                        return ToolResult.from_error("SQL execution tool not found.")
                    else:
                        # The model returned text that is not a SQL query, so we treat it as a successful natural language response.
                        return ToolResult(result={"response": sql_query})
    return ToolResult.from_error(error="No valid response from agent.")

  async def add_new_contract(self, file_path: str) -> ToolResult:
      """Adds a new contract by processing a file.

      Args:
          file_path: The absolute path to the contract PDF file.

      Returns:
          A ToolResult indicating the success or failure of the operation.
      """
      readonly_context = ReadonlyContext()
      tools = await self._document_processing_toolset.get_tools(readonly_context)
      process_document_tool = tools[0]

      return await process_document_tool._call(readonly_context, file_path=file_path)

  async def close(self):
    """Closes the agent and its underlying toolsets."""
    await self._bigquery_toolset.close()
    await self._general_insights_toolset.close()
    await self._document_processing_toolset.close()