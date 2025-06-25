import streamlit as st
import asyncio
import sys
import os

from contract_ai_agent_modules.adk.agents.main_agent.main_agent import ContractAgent
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig
from create_bigquery_schema import create_bigquery_schema

st.set_page_config(layout="wide")

st.title("Contract Management Application")

# Initialize the ContractAgent
bigquery_project_id = os.environ.get("BIGQUERY_PROJECT_ID", "walmart-chile-458918")
bigquery_location = os.environ.get("BIGQUERY_LOCATION", "us-central1")
bigquery_dataset_id = "contract_data"
bigquery_max_rows = int(os.environ.get("BIGQUERY_MAX_ROWS", 100))

# Create the BigQuery schema
create_bigquery_schema(bigquery_project_id, bigquery_dataset_id)

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
    async def get_dashboard_kpis(agent_instance: ContractAgent):
        kpis = {}

        # Fetch Contract Count by Status
        contract_count_query = "Provide the count of contracts by their status (e.g., Active, Expired, Pending)."
        count_response = await agent_instance.process_query(contract_count_query)
        if hasattr(count_response, 'is_successful') and count_response.is_successful and count_response.result and "results" in count_response.result:
            # Assuming the result is a list of dicts like [{"status": "Active", "count": 150}]
            contract_counts = {item.get("status", "Unknown"): item.get("count", 0) for item in count_response.result["results"]}
            kpis["contract_counts"] = contract_counts
        else:
            error_message = count_response.error if hasattr(count_response, 'is_successful') else 'Unknown error'
            st.warning(f"Could not fetch contract counts: {error_message}")
            kpis["contract_counts"] = {"Active": 0, "Expired": 0, "Pending": 0} # Default to 0

        # Fetch Average Contract Value
        avg_value_query = "What is the average contract value?"
        avg_value_response = await agent_instance.process_query(avg_value_query)
        if hasattr(avg_value_response, 'is_successful') and avg_value_response.is_successful and avg_value_response.result and "results" in avg_value_response.result:
            # Assuming the result is a list of dicts like [{"average_value": 150000}]
            # Or directly a value if the agent is smart enough to return just the number
            if avg_value_response.result["results"] and "average_value" in avg_value_response.result["results"][0]:
                kpis["average_contract_value"] = f"${avg_value_response.result['results'][0]['average_value']:,}"
            else:
                kpis["average_contract_value"] = "$0" # Default
        else:
            error_message = avg_value_response.error if hasattr(avg_value_response, 'is_successful') else 'Unknown error'
            st.warning(f"Could not fetch average contract value: {error_message}")
            kpis["average_contract_value"] = "$0" # Default

        # Fetch Upcoming Expirations
        upcoming_exp_query = "List contracts expiring soon, including their Contract_ID and End_Date."
        upcoming_exp_response = await agent_instance.process_query(upcoming_exp_query)
        if hasattr(upcoming_exp_response, 'is_successful') and upcoming_exp_response.is_successful and upcoming_exp_response.result and "results" in upcoming_exp_response.result:
            # Assuming result is list of dicts like [{"Contract_ID": "C001", "End_Date": "2025-07-15"}]
            kpis["upcoming_expirations"] = upcoming_exp_response.result["results"]
        else:
            error_message = upcoming_exp_response.error if hasattr(upcoming_exp_response, 'is_successful') else 'Unknown error'
            st.warning(f"Could not fetch upcoming expirations: {error_message}")
            kpis["upcoming_expirations"] = [] # Default to empty list

        # Fetch Total Penalty Amounts
        total_penalties_query = "What is the total sum of all penalty amounts?"
        total_penalties_response = await agent_instance.process_query(total_penalties_query)
        if hasattr(total_penalties_response, 'is_successful') and total_penalties_response.is_successful and total_penalties_response.result and "results" in total_penalties_response.result:
            # Assuming result is list of dicts like [{"total_penalties": 5000}]
            if total_penalties_response.result["results"] and "total_penalties" in total_penalties_response.result["results"][0]:
                kpis["total_penalty_amounts"] = f"${total_penalties_response.result['results'][0]['total_penalties']:,}"
            else:
                kpis["total_penalty_amounts"] = "$0" # Default
        else:
            error_message = total_penalties_response.error if hasattr(total_penalties_response, 'is_successful') else 'Unknown error'
            st.warning(f"Could not fetch total penalty amounts: {error_message}")
            kpis["total_penalty_amounts"] = "$0" # Default
        
        return kpis

    # Fetch dashboard KPIs
    dashboard_kpis = asyncio.run(get_dashboard_kpis(agent))

    st.subheader("Contract Count by Status")
    st.bar_chart(dashboard_kpis["contract_counts"])

    st.subheader("Average Contract Value")
    st.metric(label="Average Value", value=dashboard_kpis["average_contract_value"])

    st.subheader("Upcoming Expirations")
    st.write("List of contracts expiring soon...")
    if dashboard_kpis["upcoming_expirations"]:
        st.table(dashboard_kpis["upcoming_expirations"])
    else:
        st.info("No upcoming expirations found.")

    st.subheader("Total Penalty Amounts")
    st.metric(label="Total Penalties", value=dashboard_kpis["total_penalty_amounts"])

elif page == "Alerts":
    st.header("Alerts")
    st.write("This section will display alerts for contract expirations, warranties, etc.")

    async def get_alerts_data_from_agent(agent_instance: ContractAgent):
        query_string = "List all active alerts, including their Alert_Type, Contract_ID, and Date."
        response = await agent_instance.process_query(query_string)

        if hasattr(response, 'is_successful') and response.is_successful and response.result and "results" in response.result:
            return response.result["results"]
        else:
            error_message = response.error if hasattr(response, 'is_successful') else 'Unknown error'
            st.warning(f"Could not fetch alerts data: {error_message}")
            return []

    alerts_data = asyncio.run(get_alerts_data_from_agent(agent))

    if alerts_data:
        st.table(alerts_data)
    else:
        st.info("No new alerts at the moment.")

elif page == "Contracts":
    st.header("Contracts")
    st.write("This section will list all contracts and allow for detailed viewing and searching.")

    # Function to fetch contracts data using the agent
    async def get_contracts_data_from_agent(agent_instance: ContractAgent):
        query_string = "List all contracts with their Contract_ID, Contract_Type, Provider, Company, Business_Unit, and Price."
        response = await agent_instance.process_query(query_string)
        
        if hasattr(response, 'is_successful') and response.is_successful and response.result and "results" in response.result:
            # Convert list of dictionaries to dictionary of lists for st.dataframe
            data_list_of_dicts = response.result["results"]
            if not data_list_of_dicts:
                return {} # Return empty if no results
            
            # Assuming all dictionaries have the same keys
            keys = data_list_of_dicts[0].keys()
            contracts_data = {key: [d[key] for d in data_list_of_dicts] for key in keys}
            return contracts_data
        else:
            error_message = response.error if hasattr(response, 'is_successful') else 'Unknown error'
            st.error(f"Failed to fetch contracts data: {error_message}")
            return {} # Return empty dictionary on failure

    # Fetch data for the contracts section
    contracts_data = asyncio.run(get_contracts_data_from_agent(agent))
    
    if contracts_data:
        st.dataframe(contracts_data)
    else:
        st.info("No contract data available or failed to fetch data.")

    st.subheader("Search and Filter Contracts")
    search_term = st.text_input("Search by any attribute")
    
    # Ensure contracts_data is not empty before trying to get unique values
    if contracts_data:
        company_filter = st.selectbox("Filter by Company", ["All"] + sorted(list(set(contracts_data.get("Company", [])))))
        bu_filter = st.selectbox("Filter by Business Unit", ["All"] + sorted(list(set(contracts_data.get("Business Unit", [])))))
    else:
        company_filter = st.selectbox("Filter by Company", ["All"])
        bu_filter = st.selectbox("Filter by Business Unit", ["All"])

    # Placeholder for price histogram - this will require a more complex query
    st.subheader("Price Histogram by Service Type and Provider")
    # For now, keep static or implement a simple query if possible
    st.bar_chart({"Service": 300000, "Supply": 170000, "Consulting": 200000})

    st.subheader("Detailed Contract View (Select a contract from the list above)")
    
    # Use a selectbox for contract ID if contracts_data is available
    if contracts_data and "Contract ID" in contracts_data:
        selected_contract_id = st.selectbox("Select Contract ID for details", [""] + contracts_data["Contract ID"])
    else:
        selected_contract_id = st.text_input("Enter Contract ID for details (e.g., C001)")

    if selected_contract_id:
        async def get_contract_details_from_agent(agent_instance: ContractAgent, contract_id: str):
            query_string = f"Provide all details for Contract_ID '{contract_id}'."
            response = await agent_instance.process_query(query_string)
            
            if hasattr(response, 'is_successful') and response.is_successful and response.result and "results" in response.result:
                # Assuming the result is a list of dictionaries, and we want the first one
                if response.result["results"]:
                    return response.result["results"][0]
            else:
                error_message = response.error if hasattr(response, 'is_successful') else 'Unknown error'
                st.error(f"Failed to fetch details for Contract ID {contract_id}: {error_message}")
            return {}

        contract_details = asyncio.run(get_contract_details_from_agent(agent, selected_contract_id))
        if contract_details:
            st.json(contract_details)
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