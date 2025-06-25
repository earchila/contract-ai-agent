import streamlit as st
import asyncio
import sys
import os
import logging

from contract_ai_agent_modules.adk.agents.main_agent.main_agent import ContractAgent
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig
from create_bigquery_schema import create_bigquery_schema
from contract_ai_agent_modules.bigquery_client import BigQueryClient
import contract_ai_agent_modules.queries as queries
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="wide")

st.title("Contract Management Application")

# Initialize the ContractAgent and BigQueryClient
bigquery_project_id = os.environ.get("BIGQUERY_PROJECT_ID", "walmart-chile-458918")
bigquery_location = os.environ.get("BIGQUERY_LOCATION", "us-central1")
bigquery_dataset_id = "contract_data"
bigquery_max_rows = int(os.environ.get("BIGQUERY_MAX_ROWS", 100))

# Create the BigQuery schema
create_bigquery_schema(bigquery_project_id, bigquery_dataset_id)

bigquery_client = BigQueryClient(project_id=bigquery_project_id, dataset_id=bigquery_dataset_id)

bigquery_credentials = BigQueryCredentialsConfig(project_id=bigquery_project_id, location=bigquery_location)
bigquery_tool_config = BigQueryToolConfig(max_rows=bigquery_max_rows, default_dataset_id=bigquery_dataset_id, default_table_id="contracts") # Limit results for display
agent = ContractAgent(
    bigquery_credentials_config=bigquery_credentials,
    bigquery_tool_config=bigquery_tool_config
)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Alerts", "Contracts", "Agent Interaction"])

if page == "Dashboard":
    st.header("Dashboard - Key Performance Indicators")
    st.write("This section will display various KPIs related to contracts.")

    # Fetch and display KPIs
    contract_counts_df = bigquery_client.query_to_dataframe(queries.CONTRACT_COUNT_QUERY)
    if not contract_counts_df.empty:
        contract_counts = {row['status']: row['contract_count'] for index, row in contract_counts_df.iterrows()}
        st.subheader("Contract Count by Status")
        st.bar_chart(contract_counts)
    else:
        st.warning("Could not fetch contract counts.")

    avg_value_df = bigquery_client.query_to_dataframe(queries.AVERAGE_CONTRACT_VALUE_QUERY)
    if not avg_value_df.empty:
        avg_value = avg_value_df['average_value'][0]
        st.subheader("Average Contract Value")
        st.metric(label="Average Value", value=f"${avg_value:,.2f}")
    else:
        st.warning("Could not fetch average contract value.")

    upcoming_expirations_df = bigquery_client.query_to_dataframe(queries.UPCOMING_EXPIRATIONS_QUERY)
    st.subheader("Upcoming Expirations")
    if not upcoming_expirations_df.empty:
        st.table(upcoming_expirations_df)
    else:
        st.info("No upcoming expirations found.")

    total_penalties_df = bigquery_client.query_to_dataframe(queries.TOTAL_PENALTY_AMOUNTS_QUERY)
    if not total_penalties_df.empty:
        total_penalties = total_penalties_df['total_penalties'][0]
        st.subheader("Total Penalty Amounts")
        st.metric(label="Total Penalties", value=f"${total_penalties:,.2f}")
    else:
        st.warning("Could not fetch total penalty amounts.")

elif page == "Alerts":
    st.header("Alerts")
    st.write("This section will display alerts for contract expirations, warranties, etc.")
    alerts_df = bigquery_client.query_to_dataframe(queries.ALERTS_QUERY)
    if not alerts_df.empty:
        st.table(alerts_df)
    else:
        st.info("No new alerts at the moment.")

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