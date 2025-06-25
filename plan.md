# Plan for Integrating Gemini with BigQuery

This document outlines the plan to resolve the BigQuery integration issue in the Contract AI Agent project.

## 1. Diagnosis

The root cause of the issue is a `404 Not Found` error when the agent attempts to access BigQuery. The error message `Not found: Dataset walmart-chile-458918:walmart-chile-458918.contract_data` indicates that the BigQuery client is being passed an incorrect dataset ID.

The investigation revealed that in `main.py`, the `BigQueryToolConfig` is initialized with `default_dataset_id` set to `"walmart-chile-458918.contract_data"`. The correct value should be just `"contract_data"`, as the project ID is handled separately by the BigQuery client.

## 2. Technical Plan

The following steps will be taken to resolve the issue:

### 2.1. Modify the Configuration

-   **File:** `main.py`
-   **Change:** Modify line 20 to correct the `default_dataset_id`.

    ```python
    # Before
    bigquery_tool_config = BigQueryToolConfig(max_rows=bigquery_max_rows, default_dataset_id="walmart-chile-458918.contract_data")

    # After
    bigquery_tool_config = BigQueryToolConfig(max_rows=bigquery_max_rows, default_dataset_id="contract_data")
    ```

### 2.2. Verification

After the code change is applied, the user will need to restart the Streamlit application. The "Dataset not found" errors should be resolved, and the application's dashboard should correctly display data from the BigQuery tables.

## 3. Architecture Diagram

The following Mermaid diagram illustrates the corrected configuration flow:

```mermaid
graph TD
    subgraph Configuration in main.py
        A[BIGQUERY_PROJECT_ID env var] --> B(bigquery_project_id)
        C[BIGQUERY_LOCATION env var] --> D(bigquery_location)
        E["contract_data" string] --> F(default_dataset_id)
    end

    subgraph Initialization
        B --> G[BigQueryCredentialsConfig]
        D --> G
        F --> H[BigQueryToolConfig]
    end

    subgraph Agent
        G --> I[ContractAgent]
        H --> I
    end

    I --> J{BigQuery Toolset}
    J --> K[BigQuery Client]

    K -- Uses correct project and dataset --> L((BigQuery API))