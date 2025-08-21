import datetime
import json
from google.cloud import bigquery

def populate_dummy_data(project_id, dataset_id):
    """
    Populates the BigQuery tables with dummy data.
    """
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    # Dummy data for the 'contracts' table
    contracts_data = [
        {
            "contract_id": "C001",
            "contract_type": "Service",
            "service_detail": "IT Support",
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
            "contract_date": "2023-01-01",
            "rut_brand": "76.123.456-7",
            "provider": "Tech Solutions Inc.",
            "legal_representatives": "John Doe",
            "contract_manager": "Jane Smith",
            "financials": json.dumps({"currency": "USD", "payment_terms": "Net 30"}),
            "exit_clause": "30-day notice required for termination.",
            "general_conditions": "Standard service agreement conditions apply.",
            "company": "Walmart Chile",
            "business_unit": "IT",
            "price": 120000.00,
            "ocr_text_ref": "gs://contract-pdfs/C001.pdf",
        },
        {
            "contract_id": "C002",
            "contract_type": "Supply",
            "service_detail": "Office Supplies",
            "start_date": "2024-03-15",
            "end_date": "2025-03-14",
            "contract_date": "2024-03-01",
            "rut_brand": "77.234.567-8",
            "provider": "Office Depot",
            "legal_representatives": "Peter Jones",
            "contract_manager": "Emily White",
            "financials": json.dumps({"currency": "CLP", "payment_terms": "Net 60"}),
            "exit_clause": "None",
            "general_conditions": "Standard supply agreement.",
            "company": "Walmart Chile",
            "business_unit": "Administration",
            "price": 5000000.00,
            "ocr_text_ref": "gs://contract-pdfs/C002.pdf",
        },
    ]

    # Dummy data for the 'slas' table
    slas_data = [
        {
            "sla_id": "SLA001",
            "contract_id": "C001",
            "sla_description": "99.9% Uptime Guarantee",
            "threshold": 99.9,
            "unit": "Percentage",
            "breach_condition": "Uptime < 99.9%",
        },
        {
            "sla_id": "SLA002",
            "contract_id": "C001",
            "sla_description": "4-hour response time for critical issues",
            "threshold": 4,
            "unit": "Hours",
            "breach_condition": "Response time > 4 hours",
        },
    ]

    # Dummy data for the 'penalties' table
    penalties_data = [
        {
            "penalty_id": "P001",
            "contract_id": "C001",
            "penalty_description": "5% fee reduction for failing uptime SLA",
            "penalty_amount": 6000.00,
            "trigger_condition": "SLA001 breached",
        },
    ]

    # Dummy data for the 'alerts' table
    alerts_data = [
        {
            "alert_id": "A001",
            "contract_id": "C002",
            "alert_type": "Expiration",
            "alert_date": "2025-02-14",
            "status": "Active",
            "description": "Contract C002 is expiring in 30 days.",
        },
    ]

    tables_data = {
        "contracts": contracts_data,
        "slas": slas_data,
        "penalties": penalties_data,
        "alerts": alerts_data,
    }

    for table_id, data in tables_data.items():
        table_ref = dataset_ref.table(table_id)
        try:
            errors = client.insert_rows_json(table_ref, data)
            if errors == []:
                print(f"Successfully inserted {len(data)} rows into {table_id}.")
            else:
                print(f"Errors occurred while inserting rows into {table_id}: {errors}")
        except Exception as e:
            print(f"Error inserting data into table {table_id}: {e}")

if __name__ == "__main__":
    project_id = "walmart-chile-458918"
    dataset_id = "contract_data"
    populate_dummy_data(project_id, dataset_id)
    print("Dummy data population script finished.")