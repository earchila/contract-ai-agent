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
CONTRACT_COUNT_QUERY = """
SELECT
  CASE
    WHEN CURRENT_DATE() BETWEEN start_date AND end_date THEN 'Active'
    WHEN CURRENT_DATE() > end_date THEN 'Expired'
    ELSE 'Pending'
  END AS status,
  COUNT(contract_id) AS contract_count
FROM `contract_data.contracts`
GROUP BY
  status
"""

AVERAGE_CONTRACT_VALUE_QUERY = "SELECT AVG(price) as average_value FROM `contract_data.contracts`"

UPCOMING_EXPIRATIONS_QUERY = "SELECT contract_id, end_date FROM `contract_data.contracts` WHERE end_date BETWEEN CURRENT_DATE() AND DATE_ADD(CURRENT_DATE(), INTERVAL 90 DAY)"

TOTAL_PENALTY_AMOUNTS_QUERY = "SELECT SUM(penalty_amount) as total_penalties FROM `contract_data.penalties`"

# Alerts Queries
ALERTS_QUERY = "SELECT * FROM `contract_data.alerts`"

# Contracts Queries
CONTRACTS_QUERY = "SELECT * FROM `contract_data.contracts`"

def get_contract_details_query(contract_id: str) -> str:
    """Returns the query to get the details of a specific contract."""
    return f"SELECT * FROM `contract_data.contracts` WHERE contract_id = '{contract_id}'"