<<<<<<< HEAD
# Contract Management Web Application Plan

This document outlines the plan for developing a web application to manage contracts, featuring a comprehensive frontend, a Python-based backend leveraging Google's Gemini agents, and BigQuery for data storage.

## Frontend Technology Recommendation

Given the constraint of not using JavaScript or similar technologies and the requirement for a Python-based frontend, the following frameworks are recommended:

*   **Streamlit**: Excellent for quickly building interactive data applications and dashboards purely in Python. It's well-suited for visualizing KPIs, charts, and displaying tabular data. Its simplicity allows for rapid development.
*   **Dash (Plotly)**: Also a Python framework for building analytical web applications. It offers more control over the layout and styling compared to Streamlit and is built on top of Flask, Plotly.js, and React.js, but abstracts away the JavaScript, allowing you to write everything in Python.

For this plan, we will proceed assuming **Streamlit** for its ease of use and rapid prototyping capabilities, which aligns well with defining KPIs and iterating on the dashboard.

## Detailed Plan

### 1. Frontend (Streamlit Application)

The Streamlit application will serve as the user interface, providing the following components:

*   **1.1 Dashboard**:
    *   **KPIs**:
        *   Contract count by status (active, expired, pending) - visualized as a pie chart or bar chart.
        *   Average contract value - displayed as a single metric or a bar chart showing distribution.
        *   Upcoming expirations - a list or table of contracts expiring within a defined period (e.g., next 30/60/90 days).
        *   Total penalty amounts - a single metric or a time-series chart showing trends.
    *   **Visualization**: Interactive charts (e.g., bar charts, pie charts, line charts) using Streamlit's native charting capabilities (which leverage Plotly, Matplotlib, or Altair).
*   **1.2 Alerts**:
    *   A dedicated section to display critical alerts such as contract expirations, warranty expiry, and other predefined critical dates.
    *   Alerts will be fetched from the backend based on contract data and predefined rules.
*   **1.3 Contracts Section**:
    *   **Contract List/Table**: Display all contracts with key attributes visible.
    *   **Price Histogram**: A histogram visualizing price distribution by type of service and provider, allowing users to filter.
    *   **Detailed Contract View**: When a contract is selected, display all attributes: Contract ID, Contract type, Service Detail, Life (From x date to y date), Date, Rut (Brand), Providor, Legal representatives, Contract Manager, Penalties, Financials, SLAs, Penalties, Exit clause, General conditions, Company, and Business Unit.
    *   **Search and Segmentation**: Implement search functionality across all contract attributes. Allow filtering and segmentation by Company and Business Unit.
    *   **Classification**: Visual representation (e.g., dropdowns, filters) for classification by Company and Business Unit.
*   **1.4 Agent Interaction**:
    *   A chat-like interface where users can type questions or commands.
    *   This interface will send user queries to the Gemini backend agent and display the agent's responses.
    *   Similar to a conversational AI interface, allowing for natural language interaction with contract data.

### 2. Backend (Gemini - Python Agents)

The backend will be built using Python, leveraging the Vertex Agent ADK for Gemini. It will consist of a multi-tool agent architecture.

*   **2.1 Main Orchestration Agent**:
    *   Receives requests from the frontend (e.g., user queries from the chat, requests for KPI data, contract details).
    *   Determines the intent of the request and routes it to the appropriate specialized agent/tool.
    *   Manages the flow of information between the frontend, specialized agents, and BigQuery.
*   **2.2 Specialized Agents/Tools**:
    *   **Breach Analysis Agent/Tool**:
        *   **Functionality**: Reviews contract information in BigQuery (for a specific contract or all contracts) against predefined SLAs and conditions.
        *   **Input**: Contract ID (optional, for specific contract), date range, type of breach to analyze.
        *   **Output**: Identification of breaches, details of the breached clauses, and relevant contract information.
    *   **Penalty Analysis Agent/Tool**:
        *   **Functionality**: Reviews contract information in BigQuery (for a specific contract or all contracts) to identify applicable penalties based on defined penalty clauses and conditions.
        *   **Input**: Contract ID (optional), breach details (if linked from Breach Analysis), date range.
        *   **Output**: Identified penalties, calculation of penalty amounts, and reference to relevant contract terms.
    *   **General Insights Agent/Tool ("Talk with the Contract")**:
        *   **Functionality**: Answers general questions about contracts by accessing and interpreting data from BigQuery. This will involve natural language understanding and generation.
        *   **Input**: Natural language query from the user.
        *   **Output**: Concise and relevant answers based on the contract data. This agent will likely need access to the raw OCR-processed text or a highly structured representation of the contract content.
    *   **Data Retrieval/Querying Tool**: A foundational tool used by all agents to interact with BigQuery, abstracting the SQL queries.

### 3. Data (BigQuery)

BigQuery will serve as the primary data warehouse for all contract-related information.

*   **3.1 BigQuery Dataset Schema Definition**:
    *   **`contracts` Table**:
        *   `contract_id` (STRING, PRIMARY KEY)
        *   `contract_type` (STRING)
        *   `service_detail` (STRING)
        *   `start_date` (DATE)
        *   `end_date` (DATE)
        *   `contract_date` (DATE)
        *   `rut_brand` (STRING)
        *   `provider` (STRING)
        *   `legal_representatives` (STRING)
        *   `contract_manager` (STRING)
        *   `financials` (JSON/STRUCT or separate fields for amounts, currency, etc.)
        *   `exit_clause` (STRING/TEXT)
        *   `general_conditions` (STRING/TEXT)
        *   `company` (STRING)
        *   `business_unit` (STRING)
        *   `price` (NUMERIC) - for price histogram
        *   `ocr_text_ref` (STRING) - Reference to where the full OCR text is stored (e.g., GCS path or a separate BigQuery table for large texts).
    *   **`slas` Table**:
        *   `sla_id` (STRING, PRIMARY KEY)
        *   `contract_id` (STRING, FOREIGN KEY to `contracts`)
        *   `sla_description` (STRING)
        *   `threshold` (NUMERIC/STRING, depending on SLA type)
        *   `unit` (STRING, e.g., "days", "%")
        *   `breach_condition` (STRING/TEXT)
    *   **`penalties` Table**:
        *   `penalty_id` (STRING, PRIMARY KEY)
        *   `contract_id` (STRING, FOREIGN KEY to `contracts`)
        *   `penalty_description` (STRING)
        *   `penalty_amount_formula` (STRING/TEXT) - e.g., "10% of monthly fee"
        *   `trigger_condition` (STRING/TEXT)
    *   **`alerts` Table (or derived from `contracts` and `slas`)**:
        *   `alert_id` (STRING, PRIMARY KEY)
        *   `contract_id` (STRING, FOREIGN KEY)
        *   `alert_type` (STRING, e.g., "expiration", "warranty_expiry", "SLA_breach_risk")
        *   `alert_date` (DATE)
        *   `status` (STRING, e.g., "active", "resolved")
        *   `description` (STRING)
    *   **`kpis` Table (or derived views)**:
        *   Views or materialized views in BigQuery to pre-calculate KPIs for faster dashboard loading.

*   **3.2 Data Ingestion**:
    *   Assumption: Contracts are already scanned and processed by OCR.
    *   A process (e.g., Cloud Functions, Dataflow) will be needed to ingest the OCR-processed data into the defined BigQuery schema. This is outside the scope of this plan but is a necessary prerequisite.

### 4. Overall Architecture Diagram

```mermaid
graph TD
    User -->|Accesses| Frontend[Streamlit Web App]
    Frontend -->|Displays Data, Sends Queries| Backend[Python Backend (Gemini Agents)]

    subgraph Frontend Components
        Frontend --> Dashboard[1.1 Dashboard (KPIs, Charts)]
        Frontend --> Alerts[1.2 Alerts]
        Frontend --> ContractsSection[1.3 Contracts Section]
        Frontend --> AgentInteraction[1.4 Agent Interaction (Chat)]
    end

    subgraph Backend Components
        Backend --> MainAgent[2.1 Main Orchestration Agent]
        MainAgent --> BreachAnalysis[2.2.1 Breach Analysis Agent/Tool]
        MainAgent --> PenaltyAnalysis[2.2.2 Penalty Analysis Agent/Tool]
        MainAgent --> GeneralInsights[2.2.3 General Insights Agent/Tool]
        MainAgent --> DataTool[2.2.4 Data Retrieval/Querying Tool]
    end

    DataTool --> BigQuery[3.1 BigQuery Database]
    BigQuery -->|Stores| ContractsTable[3.1.1 contracts]
    BigQuery -->|Stores| SLATable[3.1.2 slas]
    BigQuery -->|Stores| PenaltiesTable[3.1.3 penalties]
    BigQuery -->|Stores| AlertsTable[3.1.4 alerts]
    BigQuery -->|Stores| KPIsViews[3.1.5 kpis (Views)]

    OCR_Process[OCR Processing] -->|Ingests Data| BigQuery
```

### 5. Implementation Steps (High-Level)

1.  **BigQuery Schema Definition**: Finalize and create the BigQuery dataset and tables.
2.  **Data Ingestion Pipeline**: Set up a process to load OCR-processed contract data into BigQuery.
3.  **Backend Development**:
    *   Develop the `Data Retrieval/Querying Tool` to interact with BigQuery. This will be implemented ADK BigQuery Tools
    *   Implement the `Breach Analysis`, `Penalty Analysis`, and `General Insights` agents using Vertex Agent ADK.
    *   Develop the `Main Orchestration Agent` to route requests.
4.  **Frontend Development**:
    *   Set up the Streamlit application.
    *   Develop the Dashboard, Alerts, and Contracts sections, connecting them to the backend APIs.
    *   Implement the Agent Interaction chat interface.
5.  **Deployment**: Deploy the Streamlit app and Python backend agents (e.g., on Google Cloud Run, App Engine, or Vertex AI Endpoints).
=======
# contract-ai-agent
Contract AI Dashboard &amp; Agent
>>>>>>> d6328acf47c9de066b24337e3a9dcf2f67168317
