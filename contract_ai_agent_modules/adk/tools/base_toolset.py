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
from typing import Awaitable, Callable, List, Optional

from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool


ToolPredicate = Callable[[BaseTool, ReadonlyContext], bool]


class BaseToolset(abc.ABC):
  """Base class for all toolsets."""

  @abc.abstractmethod
  async def get_tools(
      self, readonly_context: Optional[ReadonlyContext] = None
  ) -> List[BaseTool]:
    """Gets the tools from the toolset.

    Args:
      readonly_context: The readonly context.

    Returns:
      A list of tools.
    """

  @abc.abstractmethod
  async def close(self) -> Awaitable[None]:
    """Closes the toolset."""