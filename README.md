# Contract AI Agent

This project is a contract management application that uses a Streamlit frontend, a Python backend with Google Gemini, and a BigQuery database. It also includes a Node.js-based MCP server for contract analysis.

## How to Run the Application

### 1. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Authentication

Authenticate with the Google Cloud CLI to access BigQuery:

```bash
gcloud auth application-default login
```

### 3. Run the Contract Analyzer Server

The contract analyzer is a Node.js server. To run it, first install its dependencies:

```bash
cd contract-ai-agent
npm install
```

Then, start the server:

```bash
npm start
```

This server provides tools for parsing and extracting data from contract documents.

### 4. Run the Streamlit Application

In a separate terminal, start the Streamlit application from the project's root directory:

```bash
streamlit run main.py
```

The application will open in your browser.

### 5. Configure Vertex AI (for Gemini Model)

The application uses Google Gemini models via Vertex AI. Create a `.env` file in the root directory of the project and add the following variables:

```
PROJECT_ID="YOUR_GCP_PROJECT_ID"
VERTEX_AI_LOCATION="YOUR_VERTEX_AI_REGION" # e.g., us-central1
```

Replace `YOUR_GCP_PROJECT_ID` with your Google Cloud Project ID and `YOUR_VERTEX_AI_REGION` with the region where your Gemini model is deployed (e.g., `us-central1`). The default model used is `gemini-2.5-flash`.
```