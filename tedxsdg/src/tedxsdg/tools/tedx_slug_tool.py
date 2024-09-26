# tools/tedx_slug_tool.py

import logging
import csv
from typing import Any, Dict, Optional
from langchain.tools import StructuredTool

logger = logging.getLogger(__name__)

class TEDxSlugTool(StructuredTool):
    name: str = "tedx_slug"
    description: str = "Retrieves TEDx content details based on a provided slug."

    def __init__(self, llm_config: Dict[str, Any], embedder_config: Dict[str, Any], data_path: Optional[str] = None):
        if not llm_config or not embedder_config:
            raise ValueError("Missing LLM configuration or Embedder configuration.")
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path or 'data/github-mauropelucchi-tedx_dataset-update_2024-details.csv'
        self.csv_data = self._load_csv_data()  # Load CSV data upon initialization

    def _load_csv_data(self) -> Dict[str, Dict[str, Any]]:
        """Load CSV data directly without dependency on TEDxSearchTool."""
        try:
            slug_index = {}
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    slug = row.get('slug', '').strip()
                    if slug:
                        slug_index[slug] = row
            logger.debug(f"Loaded {len(slug_index)} slugs from CSV file.")
            return slug_index
        except FileNotFoundError:
            logger.error(f"CSV file not found at path: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}", exc_info=True)
            raise

    def _run(self, slug: str) -> str:
        """Retrieve data for the given slug."""
        if not slug:
            return "Error: No slug provided."

        row = self.csv_data.get(slug)
        if not row:
            return f"No data found for slug '{slug}'. Please ensure the slug is correct."

        return f"Final Answer: Data for slug '{slug}':\n{row}"
