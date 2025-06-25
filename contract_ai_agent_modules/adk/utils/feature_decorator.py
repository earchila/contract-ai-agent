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
import logging
from typing import Any, Callable, TypeVar

_LOGGER = logging.getLogger(__name__)
_F = TypeVar("_F", bound=Callable[..., Any])


def experimental(f: _F) -> _F:
  """Decorator for experimental features.

  Args:
    f: The function to decorate.

  Returns:
    The decorated function.
  """

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    _LOGGER.warning(
        "Call to experimental function/class %s. This API is experimental"
        " and may change in the future.",
        f.__qualname__,
    )
    return f(*args, **kwargs)

  return wrapper