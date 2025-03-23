
from typing import Dict
from dataclasses import dataclass
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from api.services.tenx_utils import TenxUtils
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_gpt as gpt
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaChallengeDocumentSchema
)

logger = LLPackerLogger()



class AsyncTaskAnalyzer:
    def __init__(self, **kwargs):
        self.run_stage = kwargs.get("run_stage", "dev")
        self.tu = TenxUtils(run_stage=self.run_stage)
        self.model = "gpt-4o-mini"

    def get_task_document(self, challenge_id: str) -> str:
        """Retrieve task document content from the database."""
        content, metadata = self.tu.get_challenge_document(challenge_id)
        # ipersona_challenge = IpersonaChallengeDocumentSchema()
        # content = ipersona_challenge.get_all_challenges(nopp=True, dataframe=False)
        return content

    def clean_content(self, content: str) -> str:
        """Clean and format task document content."""
        soup = BeautifulSoup(content, 'html.parser')
        content = soup.get_text()
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'[*_~`]', '', content)
        return content

    async def analyze_sections(self, content: str) -> Dict:
        """Analyze document sections asynchronously"""
        system_prompt = """
        You are an expert at analyzing documents and extracting structured information. 
        Your role is to identify and separate all tasks in the document.
        Always return your response as a JSON object.
        The number of tasks should match exactly what's in the document - don't limit or combine tasks.
        """

        user_prompt = f"""
        Analyze the following document and extract all sections, identifying each distinct task.
        Every task mentioned in the document should be extracted as a separate entry.

        Challenge Document:
        {content}

        Return a JSON object with these sections:
        {{
            "introduction": "extracted introduction text",
            "task_specifications": {{
                // Extract ALL tasks found in the document
                // Each task should be a separate key-value pair
                // The key should be the task identifier or name
                // The value should be the complete task description
            }},
        }}

        Important:
        1. Include EVERY task mentioned in the document
        2. Keep tasks separate - don't combine them
        3. Preserve the original task identifiers/numbers if present
        4. Extract the complete description for each task
        """
        # return await get_openai_response_async(system_prompt, user_prompt, self.model, run_stage=self.run_stage)
        return gpt.get_openai_response_async(system_prompt, user_prompt)

    