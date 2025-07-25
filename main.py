import streamlit as st
import asyncio
import sys
import os
import logging
import json
from google.cloud import storage
import tempfile

from contract_ai_agent_modules.adk.agents.main_agent.main_agent import ContractAgent
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig
from contract_ai_agent_modules.bigquery_client import BigQueryClient
import contract_ai_agent_modules.queries as queries
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
    }
    .sub-header {
        font-size: 16px;
        color: grey;
    }
    .kpi-card {
        background-color: #f9f9f9;
        border: 1px solid #e6e6e6;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-card h3 {
        margin-bottom: 10px;
        font-size: 16px;
        color: #333;
    }
    .kpi-card p {
        font-size: 36px;
        font-weight: bold;
        color: #000;
    }
    .recent-contracts {
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">LegalMind</p><p class="sub-header">Contract Analyzer</p>', unsafe_allow_html=True)


# Initialize the ContractAgent and BigQueryClient
bigquery_project_id = os.environ.get("BIGQUERY_PROJECT_ID", "walmart-chile-458918")
bigquery_location = os.environ.get("BIGQUERY_LOCATION", "us-central1")
bigquery_dataset_id = "contract_data"
bigquery_max_rows = int(os.environ.get("BIGQUERY_MAX_ROWS", 100))

bigquery_client = BigQueryClient(project_id=bigquery_project_id, dataset_id=bigquery_dataset_id)

bigquery_credentials = BigQueryCredentialsConfig(project_id=bigquery_project_id, location=bigquery_location)
bigquery_tool_config = BigQueryToolConfig(max_rows=bigquery_max_rows, default_dataset_id=bigquery_dataset_id, default_table_id="contracts") # Limit results for display
agent = ContractAgent(
    bigquery_credentials_config=bigquery_credentials,
    bigquery_tool_config=bigquery_tool_config
)

# Sidebar for navigation
st.sidebar.image("https://storage.googleapis.com/cloud-native-news/2022/03/cymbals-logo-1-1024x576.png", width=150)
page = st.sidebar.radio("Go to", ["Contracts", "Analyze new Contract", "Agent Interaction"])

def format_agent_response(result):
    """Formats the agent's response for display in the Streamlit UI."""
    if isinstance(result, dict):
        if 'results' in result and isinstance(result['results'], list):
            # Format SQL query results into a Markdown table
            return pd.DataFrame(result['results']).to_markdown(index=False)
        
        if 'response' in result:
            try:
                # Check if the response is a JSON string for schema explanation
                data = json.loads(result['response'])
                if 'schema_explanation' in data and isinstance(data['schema_explanation'], list):
                    markdown_output = "### Database Schema\n"
                    for field in data['schema_explanation']:
                        markdown_output += f"- **`{field.get('name', 'N/A')}`** (`{field.get('type', 'N/A')}`): {field.get('description', 'N/A')}\n"
                    return markdown_output
            except (json.JSONDecodeError, TypeError):
                # If it's not a valid JSON or not the expected structure, treat as plain text
                return str(result['response'])

    if isinstance(result, list) and all(isinstance(item, dict) for item in result):
        # Handles cases where the result is a direct list of records
        return pd.DataFrame(result).to_markdown(index=False)
    
    # Fallback for any other data types
    return str(result)

def display_contract_details(contract_id):
    st.subheader(f"Contract Details: {contract_id}")
    contract_details_df = bigquery_client.query_to_dataframe(queries.get_contract_details_query(contract_id))
    if not contract_details_df.empty:
        details = contract_details_df.to_dict(orient='records')[0]
        for key, value in details.items():
            if key == "ocr_text_ref":
                if value:
                    gcs_uri = value
                    bucket_name = gcs_uri.split('/')[2]
                    file_path = '/'.join(gcs_uri.split('/')[3:])
                    url = f"https://storage.googleapis.com/{bucket_name}/{file_path}"
                    st.markdown(f"**{key.replace('_', ' ').title()}:** [View PDF]({url})")
                else:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** Not available")
            elif key == "financials":
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                try:
                    financial_data = json.loads(value)
                    for fin_key, fin_value in financial_data.items():
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**{fin_key.replace('_', ' ').title()}:** {fin_value}")
                except (json.JSONDecodeError, TypeError):
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{value}")
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    else:
        st.info(f"No detailed information found for Contract ID: {contract_id}")

def display_extracted_data(data):
    st.subheader("Extracted Contract Data")
    with st.container(border=True):
        for key, value in data.items():
            if key == "financials" and isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string if not valid JSON

            if isinstance(value, dict):
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                for sub_key, sub_value in value.items():
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**{sub_key.replace('_', ' ').title()}:** {sub_value}")
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def upload_to_gcs(uploaded_file):
    """Uploads a file to a GCS bucket."""
    bucket_name = "contract_pdfs"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(uploaded_file.name)

    blob.upload_from_file(uploaded_file)

    return f"gs://{bucket_name}/{uploaded_file.name}"

if page == "Contracts":
    st.header("Contracts")
    st.write("This section lists all contracts. Use the filters to narrow down the results and click on a contract to view its details.")
    
    contracts_df = bigquery_client.query_to_dataframe(queries.CONTRACTS_QUERY)
    
    if contracts_df.empty:
        st.info("No contract data available or failed to fetch data.")
    else:
        # --- Search and Filter ---
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("Search by any attribute")
        with col2:
            company_options = sorted([c for c in pd.Series(contracts_df["company"]).unique() if c is not None])
            company_filter = st.selectbox("Filter by Company", ["All"] + company_options)
        with col3:
            bu_options = sorted([bu for bu in pd.Series(contracts_df["business_unit"]).unique() if bu is not None])
            bu_filter = st.selectbox("Filter by Business Unit", ["All"] + bu_options)

        # --- Apply Filters ---
        filtered_df = contracts_df.copy()
        if search_term:
            search_cols = filtered_df.select_dtypes(include=['object', 'string']).columns
            filtered_df = filtered_df[
                filtered_df[search_cols].apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
            ]
        if company_filter != "All":
            filtered_df = filtered_df[filtered_df["company"] == company_filter]
        if bu_filter != "All":
            filtered_df = filtered_df[filtered_df["business_unit"] == bu_filter]

        # --- Display Table and Handle Selection ---
        st.write("Select a row to view contract details.")
        
        # Reset index to ensure selection works correctly after filtering
        filtered_df_display = filtered_df.reset_index(drop=True)
        
        selection = st.dataframe(
            filtered_df_display,
            on_select="rerun",
            selection_mode="single-row",
            key="contracts_table",
            hide_index=True
        )

        # --- Display Details in a Container ---
        if selection.selection.rows:
            selected_row_index = selection.selection.rows[0]
            selected_contract_id = filtered_df_display.iloc[selected_row_index]["contract_id"]
            with st.container(border=True):
                display_contract_details(selected_contract_id)

elif page == "Analyze new Contract":
    st.header("Analyze new Contract")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process Contract"):
            with st.spinner("Processing contract..."):
                try:
                    # 1. Upload to GCS
                    gcs_uri = upload_to_gcs(uploaded_file)
                    st.success(f"File uploaded to {gcs_uri}")

                    # 2. Save to a temporary local file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name

                    # 3. Process with MCP
                    st.info("Extracting data from the contract...")
                    result = asyncio.run(agent.add_new_contract(temp_file_path))
                    if result.is_successful:
                        extracted_data = result.result
                        # Add the GCS URI to the extracted data
                        extracted_data['ocr_text_ref'] = gcs_uri
                        
                        # Ensure 'financials' is a valid JSON string for BigQuery
                        if 'financials' in extracted_data and isinstance(extracted_data['financials'], (dict, list)):
                            extracted_data['financials'] = json.dumps(extracted_data['financials'])
                        
                        # Insert into BigQuery
                        st.info("Saving data to BigQuery...")
                        bigquery_client.insert_row("contracts", extracted_data)
                        st.success("Contract processed and saved successfully!")
                        display_extracted_data(extracted_data)
                    else:
                        st.error(f"Failed to process contract: {result.error}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    # Clean up the temporary file
                    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)


elif page == "Agent Interaction":
    st.header("Agent Interaction - Talk with Contracts")
    st.write("This section allows you to interact with the Gemini agent to ask questions about contracts.")

    user_query = st.text_area("Ask a question about contracts:")
    if st.button("Ask Agent"):
        if user_query:
            st.info(f"You asked: {user_query}")
            try:
                # Run the async process_query in a synchronous Streamlit context
                response = asyncio.run(agent.process_query(user_query))
                if hasattr(response, 'is_successful'):
                    if response.is_successful:
                        formatted_response = format_agent_response(response.result)
                        st.markdown(formatted_response, unsafe_allow_html=True)
                    else:
                        st.error(f"Agent Error: {response.error if isinstance(response.error, str) else 'Unknown error'}")
                else:
                    # Handle direct string responses
                    formatted_response = format_agent_response(response)
                    st.markdown(formatted_response, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a question.")