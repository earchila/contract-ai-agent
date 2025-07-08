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

"""This file contains the BigQuery client for the application."""

from google.cloud import bigquery
import pandas as pd
import re

class BigQueryClient:
    """A client for interacting with BigQuery."""

    def __init__(self, project_id: str, dataset_id: str):
        """Initializes the BigQuery client."""
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id

    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the results as a Pandas DataFrame."""
        try:
            query_job = self.client.query(query)
            return query_job.to_dataframe()
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()

    def insert_row(self, table_id: str, row: dict):
        """Inserts a row into the specified table."""
        table_ref = self.client.dataset(self.dataset_id).table(table_id)
        errors = self.client.insert_rows_json(table_ref, [row])
        if errors:
            print(f"Errors inserting row: {errors}")