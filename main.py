import streamlit as st
import asyncio
import sys
import os
import logging
import json
from google.cloud import storage
import importlib.resources as pkg_resources
import io
import tempfile
from cairosvg import svg2png
from PIL import Image

from contract_ai_agent_modules.adk.agents.main_agent.main_agent import ContractAgent
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from contract_ai_agent_modules.adk.agents.toolsets.bigquery.config import BigQueryToolConfig
from contract_ai_agent_modules.bigquery_client import BigQueryClient
import contract_ai_agent_modules.queries as queries
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="wide")

# Translations dictionary
translations = {
    "en": {
        "main_header": "LegalMind",
        "sub_header": "Contract Analyzer",
        "sidebar_image_not_found": "Sidebar image not found. Please ensure 'Walmart_Chile_Logo.svg' is in 'contract_ai_agent_modules/static/images/'.",
        "error_loading_sidebar_image": "Error loading sidebar image:",
        "go_to": "Go to",
        "language": "Language",
        "contracts": "Contracts",
        "analyze_new_contract": "Analyze new Contract",
        "agent_interaction": "Agent Interaction",
        "contract_details": "Contract Details:",
        "not_available": "Not available",
        "no_detailed_info": "No detailed information found for Contract ID:",
        "extracted_contract_data": "Extracted Contract Data",
        "this_section_lists_contracts": "This section lists all contracts. Use the filters to narrow down the results and click on a contract to view its details.",
        "no_contract_data_available": "No contract data available or failed to fetch data.",
        "search_by_attribute": "Search by any attribute",
        "filter_by_company": "Filter by Company",
        "all": "All",
        "filter_by_business_unit": "Filter by Business Unit",
        "select_row_to_view_details": "Select a row to view contract details.",
        "choose_pdf_file": "Choose a PDF file",
        "process_contract": "Process Contract",
        "processing_contract": "Processing contract...",
        "file_uploaded_to": "File uploaded to",
        "extracting_data": "Extracting data from the contract...",
        "saving_data_to_bigquery": "Saving data to BigQuery...",
        "contract_processed_successfully": "Contract processed and saved successfully!",
        "failed_to_process_contract": "Failed to process contract:",
        "an_error_occurred": "An error occurred:",
        "agent_interaction_header": "Agent Interaction - Talk with Contracts",
        "agent_interaction_description": "This section allows you to interact with the Gemini agent to ask questions about contracts.",
        "ask_question_about_contracts": "Ask a question about contracts:",
        "ask_agent": "Ask Agent",
        "you_asked": "You asked:",
        "agent_error": "Agent Error:",
        "unknown_error": "Unknown error",
        "unexpected_error_occurred": "An unexpected error occurred:",
        "please_enter_question": "Please enter a question.",
        "view_pdf": "View PDF",
        "database_schema": "Database Schema",
    },
    "es": {
        "main_header": "LegalMind",
        "sub_header": "Analizador de Contratos",
        "sidebar_image_not_found": "Imagen de la barra lateral no encontrada. Asegúrese de que 'Walmart_Chile_Logo.svg' esté en 'contract_ai_agent_modules/static/images/'.",
        "error_loading_sidebar_image": "Error al cargar la imagen de la barra lateral:",
        "go_to": "Ir a",
        "language": "Idioma",
        "contracts": "Contratos",
        "analyze_new_contract": "Analizar nuevo Contrato",
        "agent_interaction": "Interacción del Agente",
        "contract_details": "Detalles del Contrato:",
        "not_available": "No disponible",
        "no_detailed_info": "No se encontró información detallada para el ID de Contrato:",
        "extracted_contract_data": "Datos del Contrato Extraídos",
        "this_section_lists_contracts": "Esta sección lista todos los contratos. Use los filtros para reducir los resultados y haga clic en un contrato para ver sus detalles.",
        "no_contract_data_available": "No hay datos de contrato disponibles o falló la obtención de datos.",
        "search_by_attribute": "Buscar por cualquier atributo",
        "filter_by_company": "Filtrar por Empresa",
        "all": "Todos",
        "filter_by_business_unit": "Filtrar por Unidad de Negocio",
        "select_row_to_view_details": "Seleccione una fila para ver los detalles del contrato.",
        "choose_pdf_file": "Elegir un archivo PDF",
        "process_contract": "Procesar Contrato",
        "processing_contract": "Procesando contrato...",
        "file_uploaded_to": "Archivo subido a",
        "extracting_data": "Extrayendo datos del contrato...",
        "saving_data_to_bigquery": "Guardando datos en BigQuery...",
        "contract_processed_successfully": "Contrato procesado y guardado exitosamente!",
        "failed_to_process_contract": "Fallo al procesar el contrato:",
        "an_error_occurred": "Ocurrió un error:",
        "agent_interaction_header": "Interacción del Agente - Hablar con Contratos",
        "agent_interaction_description": "Esta sección le permite interactuar con el agente Gemini para hacer preguntas sobre contratos.",
        "ask_question_about_contracts": "Haga una pregunta sobre contratos:",
        "ask_agent": "Preguntar al Agente",
        "you_asked": "Usted preguntó:",
        "agent_error": "Error del Agente:",
        "unknown_error": "Error desconocido",
        "unexpected_error_occurred": "Ocurrió un error inesperado:",
        "please_enter_question": "Por favor, ingrese una pregunta.",
        "view_pdf": "Ver PDF",
        "database_schema": "Esquema de la Base de Datos",
    }
}

# Session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def _(key):
    return translations[st.session_state.language].get(key, key)

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
st.markdown(f'<p class="main-header">{_("main_header")}</p><p class="sub-header">{_("sub_header")}</p>', unsafe_allow_html=True)


# Initialize the ContractAgent and BigQueryClient
bigquery_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
bigquery_location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
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
# Load the image from package resources and convert SVG to PNG if necessary
try:
    with pkg_resources.open_binary('contract_ai_agent_modules.static.images', 'Walmart_Chile_Logo.svg') as f:
        svg_data = f.read()
    
    # Convert SVG to PNG
    png_data = svg2png(bytestring=svg_data, output_width=150, output_height=150) # Adjust dimensions as needed
    image_bytes = io.BytesIO(png_data)
    
    st.sidebar.image(image_bytes, width=150)
except FileNotFoundError:
    st.sidebar.warning(_("sidebar_image_not_found"))
except Exception as e:
    st.sidebar.error(f"{_('error_loading_sidebar_image')} {e}")

page = st.sidebar.radio(_("go_to"), [_("contracts"), _("analyze_new_contract"), _("agent_interaction")])

# Language selection at the bottom of the sidebar
st.sidebar.markdown("---") # Add a separator
st.sidebar.selectbox(
    _("language"),
    options=["English", "Español"],
    index=0 if st.session_state.language == 'en' else 1,
    on_change=lambda: st.session_state.update(language='en' if st.session_state.language == 'es' else 'es'),
    key="language_selector" # Add a key to prevent duplicate widget error if "Go to" is also a selectbox
)

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
                    markdown_output = f"### {_('database_schema')}\n"
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
    st.subheader(f"{_('contract_details')} {contract_id}")
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
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {_('not_available')}")
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
        st.info(f"{_('no_detailed_info')} {contract_id}")

def display_extracted_data(data):
    st.subheader(_("extracted_contract_data"))
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

if page == _("contracts"):
    st.header(_("contracts"))
    st.write(_("this_section_lists_contracts"))
    
    contracts_df = bigquery_client.query_to_dataframe(queries.CONTRACTS_QUERY)
    
    if contracts_df.empty:
        st.info(_("no_contract_data_available"))
    else:
        # --- Search and Filter ---
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input(_("search_by_attribute"))
        with col2:
            company_options = sorted([c for c in pd.Series(contracts_df["company"]).unique() if c is not None])
            company_filter = st.selectbox(_("filter_by_company"), [_("all")] + company_options)
        with col3:
            bu_options = sorted([bu for bu in pd.Series(contracts_df["business_unit"]).unique() if bu is not None])
            bu_filter = st.selectbox(_("filter_by_business_unit"), [_("all")] + bu_options)

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
        st.write(_("select_row_to_view_details"))
        
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

elif page == _("analyze_new_contract"):
    st.header(_("analyze_new_contract"))
    
    uploaded_file = st.file_uploader(_("choose_pdf_file"), type="pdf")
    
    if uploaded_file is not None:
        if st.button(_("process_contract")):
            with st.spinner(_("processing_contract")):
                try:
                    # 1. Upload to GCS
                    gcs_uri = upload_to_gcs(uploaded_file)
                    st.success(f"{_('file_uploaded_to')} {gcs_uri}")

                    # 2. Save to a temporary local file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name

                    # 3. Process with MCP
                    st.info(_("extracting_data"))
                    result = asyncio.run(agent.add_new_contract(temp_file_path))
                    if result.is_successful:
                        extracted_data = result.result
                        # Add the GCS URI to the extracted data
                        extracted_data['ocr_text_ref'] = gcs_uri
                        
                        # Ensure 'financials' is a valid JSON string for BigQuery
                        if 'financials' in extracted_data and isinstance(extracted_data['financials'], (dict, list)):
                            extracted_data['financials'] = json.dumps(extracted_data['financials'])
                        
                        # Insert into BigQuery
                        st.info(_("saving_data_to_bigquery"))
                        bigquery_client.insert_row("contracts", extracted_data)
                        st.success(_("contract_processed_successfully"))
                        display_extracted_data(extracted_data)
                    else:
                        st.error(f"{_('failed_to_process_contract')} {result.error}")

                except Exception as e:
                    st.error(f"{_('an_error_occurred')} {e}")
                finally:
                    # Clean up the temporary file
                    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)


elif page == _("agent_interaction"):
    st.header(_("agent_interaction_header"))
    st.write(_("agent_interaction_description"))

    user_query = st.text_area(_("ask_question_about_contracts"))
    if st.button(_("ask_agent")):
        if user_query:
            st.info(f"{_('you_asked')} {user_query}")
            try:
                # Run the async process_query in a synchronous Streamlit context
                response = asyncio.run(agent.process_query(user_query))
                if hasattr(response, 'is_successful'):
                    if response.is_successful:
                        formatted_response = format_agent_response(response.result)
                        st.markdown(formatted_response, unsafe_allow_html=True)
                    else:
                        st.error(f"{_('agent_error')} {response.error if isinstance(response.error, str) else _('unknown_error')}")
                else:
                    # Handle direct string responses
                    formatted_response = format_agent_response(response)
                    st.markdown(formatted_response, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"{_('unexpected_error_occurred')} {e}")
        else:
            st.warning(_("please_enter_question"))
