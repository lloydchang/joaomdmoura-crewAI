#!/usr/bin/env python

# tools/custom_tool.py

import logging
import re
from langchain.tools import StructuredTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Type, Optional
from crewai_tools import YoutubeVideoSearchTool as CrewAIYoutubeSearchTool

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

# Helper functions
def is_valid_youtube_url(url: str) -> bool:
    """
    Validates if the given URL is a valid YouTube URL using a regex pattern.
    """
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    return bool(youtube_regex.match(url))

def extract_query_string(query_input: Any) -> str:
    """
    Extracts a query string from different input types such as string, dict, or other objects.
    """
    if query_input is None or str(query_input).lower() in ['none', 'null', '']:
        return ""
    if isinstance(query_input, str):
        return query_input.strip()
    if isinstance(query_input, dict):
        # Check for multiple possible keys
        return query_input.get('search_query', query_input.get('query', query_input.get('q', '')).strip())
    return str(query_input).strip()

def prepare_youtube_search_input(input_data: Union[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Prepares the input for the youtube_search tool by extracting the search query.

    Parameters:
        input_data (str or dict): The input data containing the search query.

    Returns:
        dict: A dictionary formatted for youtube_search with the key 'search_query'.

    Raises:
        ValueError: If the input_data does not contain a valid search query.
    """
    logger.debug("Preparing YouTube search input.")
    if isinstance(input_data, str):
        # If input is a string, assume it's the search query
        search_query = input_data.strip()
        if not search_query:
            logger.error("Input string is empty.")
            raise ValueError("Input string is empty.")
        logger.debug(f"Extracted search_query from string: {search_query}")
        return {"search_query": search_query}
    
    elif isinstance(input_data, dict):
        # If input is a dictionary, look for 'search_query' key
        search_query = input_data.get('search_query')
        if isinstance(search_query, str):
            search_query = search_query.strip()
            if search_query:
                logger.debug(f"Extracted search_query from dict: {search_query}")
                return {"search_query": search_query}
        
        # If 'search_query' key is not present or invalid, try to find a string value in the dict
        for key, value in input_data.items():
            if isinstance(value, str):
                search_query = value.strip()
                if search_query:
                    logger.debug(f"Extracted search_query from key '{key}': {search_query}")
                    return {"search_query": search_query}
        
        # If no string value is found, raise an error
        logger.error("Dictionary input does not contain a valid 'search_query' string.")
        raise ValueError("Dictionary input does not contain a valid 'search_query' string.")
    
    else:
        # If input is neither string nor dict, raise an error
        logger.error("Invalid input type received. Expected string or dictionary.")
        raise ValueError("Input must be a string or a dictionary containing 'search_query'.")

# Input schemas
class DuckDuckGoSearchInput(BaseModel):
    """
    Input schema for DuckDuckGoSearchTool.
    """
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query for DuckDuckGo. Can be a string or a dictionary with a 'q' key.")

class YoutubeVideoSearchToolSchema(BaseModel):
    """
    Input schema for CustomYoutubeVideoSearchTool.
    """
    search_query: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Search query for YouTube content."
    )
    youtube_video_url: Optional[str] = Field(None, description="Optional YouTube video URL")

    class Config:
        populate_by_name = True  # Updated for Pydantic V2

class SDGAlignmentInput(BaseModel):
    """
    Input schema for SDGAlignmentTool.
    """
    idea: Union[str, Dict[str, Any]] = Field(..., description="Idea to analyze for SDG alignment")
    sdgs: List[Union[str, int]] = Field(default_factory=list, description="List of SDGs to consider")

class SustainabilityImpactInput(BaseModel):
    """
    Input schema for SustainabilityImpactAssessorTool.
    """
    project: Union[str, Dict[str, Any]] = Field(default="Unnamed Project", description="Project to assess for sustainability impact")
    metrics: List[str] = Field(default_factory=list, description="List of sustainability metrics")

# Tool classes
class DuckDuckGoSearchTool(StructuredTool):
    """
    A tool that uses DuckDuckGo to search the web.
    """
    name = "duckduckgo_search"
    description = "Searches the web using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: Union[str, Dict[str, Any]]) -> str:
        """
        Runs a DuckDuckGo search and returns the results.
        """
        query_str = extract_query_string(query)
        logger.info(f"DuckDuckGoSearchTool._run called with query: {query_str}")
        if not query_str:
            return "Error: No valid search query provided."
        search_api = DuckDuckGoSearchAPIWrapper()
        try:
            result = search_api.run(query_str)
            logger.info(f"DuckDuckGo search completed successfully for query: {query_str}")
            return f"Final Answer: DuckDuckGo Search Results for '{query_str}':\n{result}"
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}", exc_info=True)
            return f"Error during DuckDuckGo search: {str(e)}"

class CustomYoutubeVideoSearchTool(StructuredTool):
    name: str = "youtube_search"
    description: str = "Searches YouTube videos for specific content using RAG techniques"
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolSchema
    config: Dict[str, Any] = Field(default_factory=dict)
    crewai_tool: Optional[CrewAIYoutubeSearchTool] = None

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        youtube_video_url: Optional[str] = None  # This can still be passed if needed
    ):
        super().__init__()
        self.config = config or {}

        # Always initialize CrewAIYoutubeSearchTool, ignoring the youtube_video_url attribute
        self.crewai_tool = CrewAIYoutubeSearchTool(config=self.config)
        logger.debug(f"CustomYoutubeVideoSearchTool initialized")

    def _run(self, search_query: Union[str, Dict[str, Any]], **kwargs: Any) -> str:
        logger.debug(f"_run called with search_query: {search_query}, kwargs: {kwargs}")

        try:
            formatted_input = prepare_youtube_search_input(search_query)
            query_str = formatted_input["search_query"]
            logger.info(f"CustomYoutubeVideoSearchTool._run called with query_str: {query_str}")
        except ValueError as ve:
            logger.error(f"Input preparation error: {str(ve)}")
            return f"Error: {str(ve)}"

        if not query_str:
            logger.error("Error: No valid search query provided.")
            return "Error: No valid search query provided."

        # Test with simple queries to verify YouTube search functionality
        test_queries = ["cats", "dogs", "funny pets"]
        for test_query in test_queries:
            logger.debug(f"Testing query: {test_query}")
            try:
                result = self.crewai_tool.run(test_query)
                logger.info(f"Test YouTube search completed successfully for '{test_query}'")
                logger.debug(f"Search result: {result}")
                return f"Test Search Results for '{test_query}':\n{result}"

            except Exception as e:
                logger.error(f"Error during YouTube video search for query '{test_query}': {str(e)}", exc_info=True)
                return f"Error during YouTube video search for query '{test_query}': {str(e)}"

        # Perform the original query after testing
        try:
            result = self.crewai_tool.run(query_str)
            logger.info("YouTube search completed successfully")
            return f"Final Answer: YouTube Search Results for '{query_str}':\n{result}"

        except Exception as e:
            logger.error(f"Error during YouTube video search: {str(e)}", exc_info=True)
            return f"Error during YouTube video search: {str(e)}"

class SDGAlignmentTool(StructuredTool):
    """
    A tool that analyzes ideas and aligns them with the United Nations Sustainable Development Goals (SDGs).
    """
    name = "sdg_alignment"
    description = "Analyzes ideas and aligns them with UN SDGs"
    args_schema: Type[BaseModel] = SDGAlignmentInput

    def _run(self, idea: Union[str, Dict[str, Any]], sdgs: List[Union[str, int]] = []) -> str:
        idea_str = extract_query_string(idea)
        logger.info(f"SDGAlignmentTool._run called with idea: {idea_str}, sdgs: {sdgs}")
        if not idea_str:
            return "Error: No valid idea provided for SDG alignment analysis."
        
        sdgs = [str(extract_query_string(sdg)) for sdg in sdgs if extract_query_string(sdg)]
        if not sdgs:
            sdgs = ["All SDGs"]
        
        logger.info(f"Performing SDG alignment analysis for idea: {idea_str}")
        # Placeholder for actual SDG alignment logic
        # Implement the logic to align the idea with the specified SDGs here
        return f"Final Answer: SDG Alignment analysis for idea: '{idea_str}', considering SDGs: {', '.join(sdgs)}"

class SustainabilityImpactAssessorTool(StructuredTool):
    """
    A tool that assesses the potential sustainability impact of ideas and projects based on certain metrics.
    """
    name = "sustainability_impact_assessor"
    description = "Assesses the potential sustainability impact of ideas and projects"
    args_schema: Type[BaseModel] = SustainabilityImpactInput

    def _run(self, project: Union[str, Dict[str, Any]], metrics: List[str]) -> str:
        project_str = extract_query_string(project)
        logger.info(f"SustainabilityImpactAssessorTool._run called with project: {project_str}, metrics: {metrics}")
        if not project_str:
            return "Error: No valid project provided for sustainability impact assessment."
        
        metrics = [extract_query_string(metric) for metric in metrics if extract_query_string(metric)]
        if not metrics:
            return "Error: No valid sustainability metrics provided for assessment."

        logger.info(f"Performing sustainability impact assessment for project: {project_str}")
        # Placeholder for actual sustainability impact assessment logic
        # Implement the logic to assess sustainability based on the provided metrics here
        return f"Final Answer: Sustainability impact assessment for project: {project_str}, considering metrics: {', '.join(metrics)}"

def create_custom_tool(tool_name: str, config: Dict = None, youtube_video_url: Optional[str] = None) -> StructuredTool:
    """
    Factory function to create and return the desired custom tool based on the tool_name.
    """
    logger.info(f"Creating custom tool: {tool_name}")

    # Removed memory handling to prevent schema errors
    # if config and 'memory' in config:
    #     if not isinstance(config['memory'], dict):
    #         logger.warning(f"Memory field in config is invalid: {config['memory']}. Setting to an empty dictionary.")
    #         config['memory'] = {}

    tools = {
        "youtube_search": CustomYoutubeVideoSearchTool,
        "duckduckgo_search": DuckDuckGoSearchTool,
        "sdg_alignment": SDGAlignmentTool,
        "sustainability_impact_assessor": SustainabilityImpactAssessorTool,
    }
    tool_class = tools.get(tool_name)
    if tool_class is None:
        logger.warning(f"Tool '{tool_name}' not found. Using DuckDuckGoSearchTool as fallback.")
        tool = DuckDuckGoSearchTool()
    elif tool_class == CustomYoutubeVideoSearchTool:
        tool = CustomYoutubeVideoSearchTool(config=config, youtube_video_url=youtube_video_url)
    else:
        tool = tool_class()
    logger.info(f"Created tool: {tool.name}")
    return tool
