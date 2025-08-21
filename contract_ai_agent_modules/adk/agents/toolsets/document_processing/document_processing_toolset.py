from typing import List, Optional
from contract_ai_agent_modules.adk.tools.base_tool import BaseTool
from contract_ai_agent_modules.adk.tools.base_toolset import BaseToolset
from contract_ai_agent_modules.adk.agents.readonly_context import ReadonlyContext
from contract_ai_agent_modules.adk.agents.toolsets.document_processing.document_processing_tool import DocumentProcessingTool, process_document

class DocumentProcessingToolset(BaseToolset):
    def __init__(self):
        pass

    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> List[BaseTool]:
        return [DocumentProcessingTool(func=process_document)]

    async def close(self):
        pass