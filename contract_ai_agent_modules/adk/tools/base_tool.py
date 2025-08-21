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

import abc
import inspect
from typing import Any, Callable, Dict, Optional

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult


class BaseTool(abc.ABC):
  """Base class for all tools."""

  def __init__(self, func: Callable[..., Any]):
    self._func = func
    self._name = func.__name__
    self._description = inspect.getdoc(func)
    self._parameters = inspect.signature(func).parameters

  @property
  def name(self) -> str:
    return self._name

  @property
  def description(self) -> Optional[str]:
    return self._description

  @property
  def parameters(self) -> Dict[str, inspect.Parameter]:
    return self._parameters

  def to_function_declaration(self) -> "Tool":
    """Converts the tool to a Vertex AI Tool."""
    from vertexai.generative_models import FunctionDeclaration, Tool

    parameters = {
        name: {
            "type": self._get_schema_type(param.annotation),
            "description": param.kind.description
            if hasattr(param.kind, "description")
            else None,
        }
        for name, param in self.parameters.items()
        if name
        not in ["client", "readonly_context", "bigquery_tool_config"]
    }
    
    required = [
        name
        for name, param in self.parameters.items()
        if param.default == inspect.Parameter.empty
        and name
        not in ["client", "readonly_context", "bigquery_tool_config"]
    ]

    function_declaration = FunctionDeclaration(
        name=self.name,
        description=self.description,
        parameters={
            "type": "object",
            "properties": parameters,
            "required": required,
        },
    )
    return Tool(function_declarations=[function_declaration])

  def _get_schema_type(self, annotation: Any) -> str:
    """Converts a Python type annotation to a JSON Schema type."""
    if annotation == str:
        return "string"
    elif annotation == int:
        return "integer"
    elif annotation == float:
        return "number"
    elif annotation == bool:
        return "boolean"
    elif annotation == list:
        return "array"
    elif annotation == dict:
        return "object"
    else:
        return "string" # Default to string

  async def __call__(
      self, readonly_context: ReadonlyContext, **kwargs
  ) -> ToolResult:
    return await self._call(readonly_context, **kwargs)

  @abc.abstractmethod
  async def _call(
      self, readonly_context: ReadonlyContext, **kwargs
  ) -> ToolResult:
    """Calls the tool.

    Args:
      readonly_context: The readonly context.
      **kwargs: The keyword arguments to pass to the tool.

    Returns:
      The tool result.
    """