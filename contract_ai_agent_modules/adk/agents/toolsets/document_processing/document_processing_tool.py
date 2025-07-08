from typing import Dict
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.tool_result import ToolResult
from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from vertexai.generative_models import GenerativeModel, Part
import json

def process_document(file_path: str) -> Dict:
    """Processes a contract PDF to extract its data using Gemini.

    Args:
        file_path: The absolute path to the contract PDF file.

    Returns:
        A dictionary containing the extracted contract data.
    """
    pass

def validate_and_coerce_data(data: dict, schema: dict) -> dict:
    """Validates and coerces data types to match the BigQuery schema."""
    coerced_data = data.copy()
    for field, expected_type in schema.items():
        if field in coerced_data:
            value = coerced_data[field]
            if expected_type == "STRING" and isinstance(value, list):
                coerced_data[field] = ", ".join(map(str, value))
            elif expected_type == "STRING" and not isinstance(value, str):
                coerced_data[field] = str(value)
            elif expected_type == "NUMERIC" and not isinstance(value, (int, float)):
                try:
                    coerced_data[field] = float(value)
                except (ValueError, TypeError):
                    coerced_data[field] = None  # Or handle error appropriately
            elif expected_type == "JSON" and not isinstance(value, str):
                coerced_data[field] = json.dumps(value)
            # Add more type checks and coercions as needed (e.g., for DATE, TIMESTAMP)
    return coerced_data

class DocumentProcessingTool(BaseTool):
    
    BIGQUERY_SCHEMA = {
        "contract_id": "STRING",
        "contract_name": "STRING",
        "contract_type": "STRING",
        "service_detail": "STRING",
        "start_date": "DATE",
        "end_date": "DATE",
        "contract_date": "DATE",
        "rut_brand": "STRING",
        "provider": "STRING",
        "legal_representatives": "STRING",
        "contract_manager": "STRING",
        "financials": "JSON",
        "exit_clause": "STRING",
        "general_conditions": "STRING",
        "company": "STRING",
        "business_unit": "STRING",
        "price": "NUMERIC",
        "ocr_text_ref": "STRING",
    }

    async def _call(self, readonly_context: ReadonlyContext, **kwargs) -> ToolResult:
        file_path = kwargs.get("file_path")
        if not file_path:
            return ToolResult.from_error("file_path is required.")

        try:
            # 1. Read the PDF content as bytes
            with open(file_path, "rb") as f:
                pdf_content = f.read()

            # 2. Use Gemini to process the PDF directly
            model = GenerativeModel("gemini-2.5-flash")
            
            document_part = Part.from_data(
                data=pdf_content, mime_type="application/pdf"
            )
            
            prompt = """
            You are an expert in legal contract analysis. Please analyze the provided PDF document and extract the following information, returning it as a single, minified JSON object. All extracted text should be in English.:
            - contract_id
            - contract_name
            - contract_type
            - service_detail
            - start_date (in YYYY-MM-DD format)
            - end_date (in YYYY-MM-DD format)
            - contract_date (in YYYY-MM-DD format)
            - rut_brand
            - provider
            - legal_representatives
            - contract_manager
            - financials (as a JSON string)
            - exit_clause
            - general_conditions
            - company
            - business_unit
            - price (as a number)
            """
            
            response = await model.generate_content_async([document_part, prompt])
            
            # 3. Parse the JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()

            extracted_data = json.loads(response_text)

            # 4. Validate and coerce data
            validated_data = validate_and_coerce_data(extracted_data, self.BIGQUERY_SCHEMA)

            return ToolResult.success(result=validated_data)
        except Exception as e:
            return ToolResult.from_error(str(e))