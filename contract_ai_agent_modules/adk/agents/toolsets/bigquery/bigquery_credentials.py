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
from typing import Optional


@dataclasses.dataclass(frozen=True)
class BigQueryCredentialsConfig:
  """BigQuery credentials config.

  Attributes:
    project_id: The ID of the project which contains the dataset. If not set,
      the project ID will be inferred from the environment.
    location: The location of the dataset. If not set, the location will be
      inferred from the environment.
  """

  project_id: Optional[str] = None
  location: Optional[str] = None