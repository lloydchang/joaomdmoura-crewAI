# tools/sustainability_impact_tool.py

import logging
import csv
from typing import Any, Dict, List, Optional, Type, Union
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from schemas.sustainability_impact_schema import SustainabilityImpactInput
from schemas.config_schemas import LLMConfig, EmbedderConfig
from .utils import extract_query_string

logger = logging.getLogger(__name__)

class SustainabilityImpactTool(StructuredTool):
    name: str = "sustainability_impact"
    description: str = "Assesses the potential sustainability impact of ideas and projects."
    args_schema: Type[BaseModel] = SustainabilityImpactInput

    llm_config: LLMConfig = Field(exclude=True)
    embedder_config: EmbedderConfig = Field(exclude=True)
    data_path: str = Field(default='data/impact_data.csv', description="Path to the sustainability impact data CSV.")

    def __init__(self, llm_config: LLMConfig, embedder_config: EmbedderConfig, data_path: str):
        super().__init__()
        self.llm_config = llm_config
        self.embedder_config = embedder_config
        self.data_path = data_path
        self.impact_data = self._load_impact_data()

    def _load_impact_data(self) -> Dict[str, Any]:
        try:
            impact_index = {}
            with open(self.data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    impact_id = row.get('impact_id', '').strip()
                    if impact_id:
                        impact_index[impact_id] = row
            logger.debug(f"Loaded {len(impact_index)} impacts from '{self.data_path}'.")
            return impact_index
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise FileNotFoundError(f"File not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading sustainability impact data: {e}", exc_info=True)
            raise Exception("Failed to load impact data.")

    def _calculate_impact_score(self, impact_details: Dict[str, Any], relevant_metrics: List[str]) -> float:
        try:
            score_weight = float(impact_details.get('score_weight', 0))
            score = score_weight * len(relevant_metrics)
            return score
        except Exception as e:
            logger.error(f"Error calculating impact score for '{impact_details.get('impact_name')}': {e}", exc_info=True)
            return 0.0

    def _analyze(self, project: str, metrics: List[str]) -> Dict[str, float]:
        results = {}
        for impact_id, impact_details in self.impact_data.items():
            impact_metrics = impact_details.get('metrics', '').split(';')
            relevant_metrics = set(metrics).intersection(set(impact_metrics))

            if relevant_metrics:
                score = self._calculate_impact_score(impact_details, list(relevant_metrics))
                if score > 0:
                    results[impact_details['impact_name']] = score

        return results

    def _run(self, project: Union[str, Dict[str, Any]], metrics: List[str]) -> str:
        project_str = extract_query_string(project)
        if not project_str:
            return "Error: No valid project provided for sustainability impact assessment."

        metrics = [metric.strip() for metric in metrics if metric.strip()]
        if not metrics:
            return "Error: No valid sustainability metrics provided."

        logger.debug(f"Assessing sustainability impact for project: '{project_str}'")

        impact_results = self._analyze(project_str, metrics)
        if not impact_results:
            return "No relevant sustainability impacts found."

        formatted_results = "\n".join([f"{impact}: {score}" for impact, score in impact_results.items()])
        return f"Final Answer:\n{formatted_results}"