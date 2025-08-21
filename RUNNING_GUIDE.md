# Running the Contract AI Agent Application

This guide provides instructions on how to set up and run the Contract AI Agent application.

## Prerequisites

*   Python 3.9+
*   pip (Python package installer)
*   Google Cloud Platform (GCP) project with BigQuery and Cloud Storage APIs enabled.
*   Service Account Key for GCP authentication (recommended for production, or use `gcloud auth application-default login` for local development).

## Setup Instructions

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd contract-ai-agent
    ```

2.  **Create a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google Cloud Authentication:**
    The application interacts with Google Cloud BigQuery and Cloud Storage. You need to authenticate your environment.

    *   **Option 1: Application Default Credentials (for local development):**
        ```bash
        gcloud auth application-default login
        ```
        Follow the prompts to authenticate with your Google account.

    *   **Option 2: Service Account Key (for production or automated environments):**
        Download your service account key JSON file. Then, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of this file:
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
        ```
        (On Windows, use `set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"`)

5.  **Set Environment Variables:**
    The application requires certain environment variables for BigQuery configuration. Replace `YOUR_PROJECT_ID` and `YOUR_LOCATION` with your actual GCP project ID and desired BigQuery location (e.g., `us-central1`).

    ```bash
    export BIGQUERY_PROJECT_ID="YOUR_PROJECT_ID"
    export BIGQUERY_LOCATION="YOUR_LOCATION"
    export BIGQUERY_MAX_ROWS="100" # Optional: Adjust as needed
    ```
    (On Windows, use `set BIGQUERY_PROJECT_ID="YOUR_PROJECT_ID"` etc.)

    Ensure that the `contract_data` dataset exists in your BigQuery project, and a `contracts` table within it, or modify the `bigquery_dataset_id` and `default_table_id` variables in `main.py` and `contract_ai_agent_modules/adk/agents/toolsets/bigquery/config.py` accordingly.

6.  **Start the MCP Server:**
    The application relies on an MCP server for contract analysis. You need to start the `contract-analyzer` server.
    ```bash
    node /Users/archila/Documents/Cline/MCP/contract-analyzer-server/build/index.js
    ```
    *Note: The path to the `contract-analyzer-server` might vary based on your system setup.*

## Running the Application

Once all prerequisites and setup steps are completed, you can run the Streamlit application:

```bash
streamlit run main.py
```

This will open the application in your web browser.