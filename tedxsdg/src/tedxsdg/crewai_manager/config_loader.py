# crewai_manager/config_loader.py

import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str, config_type: str) -> dict:
    """
    Load YAML configuration from a given path.

    :param config_path: Path to the YAML config file
    :param config_type: Type of configuration being loaded (e.g., 'tools', 'agents', 'tasks')
    :return: Parsed YAML as a dictionary
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Loaded {config_type} configuration from '{config_path}'.")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: '{config_path}'.")
        raise
    except yaml.YAMLError as yaml_err:
        logger.error(f"YAML error loading {config_type} configuration from '{config_path}': {yaml_err}")
        raise
    except Exception as e:
        logger.error(f"Error loading {config_type} configuration from '{config_path}': {str(e)}")
        raise
