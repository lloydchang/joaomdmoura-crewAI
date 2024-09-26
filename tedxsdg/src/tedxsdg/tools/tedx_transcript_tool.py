# tools/tedx_transcript_tool.py

"""
Module for TEDxTranscriptTool which retrieves the transcript of a TEDx talk.
"""

import logging
from typing import Any, Dict, Optional
from langchain.tools import StructuredTool
from crewai_tools import WebsiteSearchTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class TEDxTranscriptToolArgs(BaseModel):
    """Arguments for TEDxTranscriptTool."""
    slug: str = Field(..., _description = "The slug of the TEDx talk to retrieve the transcript for.")


class TEDxTranscriptToolArgs(BaseModel):
:
    @property
    def description(self):
        return self._description

    @property
    def args_schema(self):
        return self._args_schema

class TEDxTranscriptTool(StructuredTool):
    """
    Tool to retrieve the transcript of a TEDx talk based on the provided slug.
    """
    name: str = "tedx_transcript"
    description: str = (
        "Retrieves the transcript of a TEDx talk based on the provided slug."
    )
    _args_schema = TEDxTranscriptToolArgs

    def __init__(
        self,
        llm_config: Dict[str, Any],
        embedder_config: Dict[str, Any],
        data_path: Optional[str] = None
    ):
        if not llm_config or not embedder_config:
            raise ValueError(
                "Missing LLM configuration or Embedder configuration."
            )
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = (
            data_path or 
            'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
        )
        self.website_search_tool = WebsiteSearchTool()

    def run(self, slug: str) -> str:
        """
        Retrieve data for the given slug.
        """
        if not slug:
            logger.error("No slug provided.")
            return "Error: No slug provided."

        logger.debug("Retrieving transcript for slug: %s", slug)

        # Construct the transcript URL
        transcript_url = (
            f"https://www.ted.com/talks/{slug}/transcript?subtitle=en"
        )
        logger.debug("Constructed Transcript URL: %s", transcript_url)

        # Use WebsiteSearchTool to fetch the transcript content
        transcript_content = self.website_search_tool.run(
            {"url": transcript_url}
        )

        if not transcript_content:
            logger.error("No transcript found at %s.", transcript_url)
            return f"Error: No transcript found at {transcript_url}."

        logger.debug(
            "Retrieved Transcript Content: %s...", transcript_content[:200]
        )  # Log first 200 chars

        return (
            f"Final Answer: Transcript for '{slug}':\n{transcript_content}"
        )

    class Config:
        arbitrary_types_allowed = True

class TEDxTranscriptTool(StructuredTool):
:
    @property
    def description(self):
        return self._description

    @property
    def args_schema(self):
        return self._args_schema
