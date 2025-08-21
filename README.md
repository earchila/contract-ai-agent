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