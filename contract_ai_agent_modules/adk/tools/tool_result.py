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

import dataclasses
from typing import Any, Dict, Optional


@dataclasses.dataclass(frozen=True)
class ToolResult:
  """Tool result.

  Attributes:
    result: The result of the tool.
    error: The error message if the tool failed.
  """

  result: Optional[Dict[str, Any]] = None
  error: Optional[str] = None

  @classmethod
  def success(cls, result: Dict[str, Any]) -> ToolResult:
    return cls(result=result)

  @classmethod
  def from_error(cls, error: str) -> ToolResult:
    return cls(error=error)

  @property
  def is_successful(self) -> bool:
    return self.error is None