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

"""This file contains all the pre-defined queries for the application."""

# Dashboard Queries
CONTRACT_COUNT_QUERY = "SELECT COUNT(contract_id) AS contract_count FROM `contract_data.contracts`"

TOTAL_PENALTY_AMOUNTS_QUERY = "SELECT SUM(penalty_amount) as total_penalties FROM `contract_data.penalties`"

RECENT_CONTRACTS_QUERY = "SELECT contract_id, contract_name, contract_type, business_unit, provider FROM `contract_data.contracts` ORDER BY start_date DESC LIMIT 10"

# Alerts Queries
ALERTS_QUERY = "SELECT * FROM `contract_data.alerts`"

# Contracts Queries
CONTRACTS_QUERY = "SELECT * FROM `contract_data.contracts`"

def get_contract_details_query(contract_id: str) -> str:
    """Returns the query to get the details of a specific contract."""
    return f"SELECT * FROM `contract_data.contracts` WHERE contract_id = '{contract_id}'"