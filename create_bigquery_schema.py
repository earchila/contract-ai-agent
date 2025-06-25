from google.cloud import bigquery

def create_bigquery_schema(project_id, dataset_id):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    # Define table schemas
    contracts_schema = [
        bigquery.SchemaField("contract_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("contract_type", "STRING"),
        bigquery.SchemaField("service_detail", "STRING"),
        bigquery.SchemaField("start_date", "DATE"),
        bigquery.SchemaField("end_date", "DATE"),
        bigquery.SchemaField("contract_date", "DATE"),
        bigquery.SchemaField("rut_brand", "STRING"),
        bigquery.SchemaField("provider", "STRING"),
        bigquery.SchemaField("legal_representatives", "STRING"),
        bigquery.SchemaField("contract_manager", "STRING"),
        bigquery.SchemaField("financials", "JSON"), # Using JSON type for flexibility
        bigquery.SchemaField("exit_clause", "STRING"),
        bigquery.SchemaField("general_conditions", "STRING"),
        bigquery.SchemaField("company", "STRING"),
        bigquery.SchemaField("business_unit", "STRING"),
        bigquery.SchemaField("price", "NUMERIC"),
        bigquery.SchemaField("ocr_text_ref", "STRING"),
    ]

    slas_schema = [
        bigquery.SchemaField("sla_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("contract_id", "STRING"),
        bigquery.SchemaField("sla_description", "STRING"),
        bigquery.SchemaField("threshold", "NUMERIC"),
        bigquery.SchemaField("unit", "STRING"),
        bigquery.SchemaField("breach_condition", "STRING"),
    ]

    penalties_schema = [
        bigquery.SchemaField("penalty_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("contract_id", "STRING"),
        bigquery.SchemaField("penalty_description", "STRING"),
        bigquery.SchemaField("penalty_amount_formula", "STRING"),
        bigquery.SchemaField("trigger_condition", "STRING"),
    ]

    alerts_schema = [
        bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("contract_id", "STRING"),
        bigquery.SchemaField("alert_type", "STRING"),
        bigquery.SchemaField("alert_date", "DATE"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("description", "STRING"),
    ]

    tables = {
        "contracts": contracts_schema,
        "slas": slas_schema,
        "penalties": penalties_schema,
        "alerts": alerts_schema,
    }

    for table_id, schema in tables.items():
        table_ref = dataset_ref.table(table_id)
        table = bigquery.Table(table_ref, schema=schema)
        try:
            table = client.create_table(table, exists_ok=True)
            print(f"Table {table.project}.{table.dataset_id}.{table.table_id} created.")
        except Exception as e:
            print(f"Error creating table {table_id}: {e}")

if __name__ == "__main__":
    project_id = "walmart-chile-458918"
    dataset_id = "contract_data"
    create_bigquery_schema(project_id, dataset_id)