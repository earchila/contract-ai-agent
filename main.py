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
page = st.sidebar.radio("Go to", ["Dashboard", "Contracts", "Add Contract", "Alerts", "Agent Interaction"])

@st.dialog("Contract Details")
def display_contract_details(contract_id):
    contract_details_df = bigquery_client.query_to_dataframe(queries.get_contract_details_query(contract_id))
    if not contract_details_df.empty:
        details = contract_details_df.to_dict(orient='records')[0]
        for key, value in details.items():
            if key == "ocr_text_ref":
                if value:
                    # Assuming the GCS URI is in the format gs://bucket_name/file_path
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

def upload_to_gcs(uploaded_file):
    """Uploads a file to a GCS bucket."""
    bucket_name = "contract_pdfs"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(uploaded_file.name)

    blob.upload_from_file(uploaded_file)

    return f"gs://{bucket_name}/{uploaded_file.name}"

if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to LegalMind. Get an overview of your contract landscape.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add New Contract"):
            st.session_state.page = "Add Contract"

    # Fetch and display KPIs
    total_contracts = 0
    contract_counts_df = bigquery_client.query_to_dataframe(queries.CONTRACT_COUNT_QUERY)
    if not contract_counts_df.empty:
        total_contracts = contract_counts_df['contract_count'].sum()

    active_alerts = 0
    alerts_df = bigquery_client.query_to_dataframe(queries.ALERTS_QUERY)
    if not alerts_df.empty:
        active_alerts = len(alerts_df)

    potential_penalties = 0
    total_penalties_df = bigquery_client.query_to_dataframe(queries.TOTAL_PENALTY_AMOUNTS_QUERY)
    if not total_penalties_df.empty:
        potential_penalties = total_penalties_df['total_penalties'][0]

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown('<div class="kpi-card"><h3>Total Contracts</h3><p>{}</p></div>'.format(total_contracts), unsafe_allow_html=True)
    with kpi2:
        st.markdown('<div class="kpi-card"><h3>Active Alerts</h3><p>{}</p></div>'.format(active_alerts), unsafe_allow_html=True)
    with kpi3:
        st.markdown('<div class="kpi-card"><h3>Potential Penalties</h3><p>${:,.2f}</p></div>'.format(potential_penalties), unsafe_allow_html=True)

    st.markdown('<div class="recent-contracts"><h3>Recent Contracts</h3></div>', unsafe_allow_html=True)
    
    recent_contracts_df = bigquery_client.query_to_dataframe(queries.RECENT_CONTRACTS_QUERY)
    if not recent_contracts_df.empty:
        for index, row in recent_contracts_df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 2])
            with col1:
                st.write(row['contract_id'])
            with col2:
                st.write(row.get('contract_name', 'N/A'))
            with col3:
                st.write(row['contract_type'])
            with col4:
                st.write(row['business_unit'])
            with col5:
                st.write(row['provider'])
            with col6:
                if st.button("View", key=f"view_{index}_{row['contract_id']}"):
                    display_contract_details(row['contract_id'])
    else:
        st.info("No contracts uploaded yet.")

elif page == "Contracts":
    st.header("Contracts")
    st.write("This section will list all contracts and allow for detailed viewing and searching.")
    contracts_df = bigquery_client.query_to_dataframe(queries.CONTRACTS_QUERY)
    
    if not contracts_df.empty:
        st.dataframe(contracts_df)
    else:
        st.info("No contract data available or failed to fetch data.")

    st.subheader("Search and Filter Contracts")
    search_term = st.text_input("Search by any attribute")
    
    if not contracts_df.empty:
        company_filter = st.selectbox("Filter by Company", ["All"] + sorted(list(contracts_df["company"].unique())))
        bu_filter = st.selectbox("Filter by Business Unit", ["All"] + sorted(list(contracts_df["business_unit"].unique())))
    else:
        company_filter = st.selectbox("Filter by Company", ["All"])
        bu_filter = st.selectbox("Filter by Business Unit", ["All"])

    st.subheader("Price Histogram by Service Type and Provider")
    st.bar_chart({"Service": 300000, "Supply": 170000, "Consulting": 200000})

    st.subheader("Detailed Contract View (Select a contract from the list above)")
    
    if not contracts_df.empty:
        selected_contract_id = st.selectbox("Select Contract ID for details", [""] + list(contracts_df["contract_id"]))
    else:
        selected_contract_id = st.text_input("Enter Contract ID for details (e.g., C001)")

    if selected_contract_id:
        contract_details_df = bigquery_client.query_to_dataframe(queries.get_contract_details_query(selected_contract_id))
        if not contract_details_df.empty:
            st.json(contract_details_df.to_dict(orient='records')[0])
        else:
            st.info(f"No detailed information found for Contract ID: {selected_contract_id}")

elif page == "Add Contract":
    st.header("Add New Contract")
    
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
                        
                        # Insert into BigQuery
                        st.info("Saving data to BigQuery...")
                        bigquery_client.insert_row("contracts", extracted_data)
                        st.success("Contract processed and saved successfully!")
                        st.json(extracted_data)
                    else:
                        st.error(f"Failed to process contract: {result.error}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    # Clean up the temporary file
                    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)

elif page == "Alerts":
    st.header("Alerts")
    st.write("This section will display alerts for contract expirations, warranties, etc.")
    alerts_df = bigquery_client.query_to_dataframe(queries.ALERTS_QUERY)
    if not alerts_df.empty:
        st.table(alerts_df)
    else:
        st.info("No new alerts at the moment.")

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
                        st.success(f"Agent Response: {response.result}")
                    else:
                        st.error(f"Agent Error: {response.error if isinstance(response.error, str) else 'Unknown error'}")
                else:
                    # Handle direct string responses
                    st.success(f"Agent Response: {response}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a question.")