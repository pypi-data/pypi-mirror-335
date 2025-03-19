import os
from pathlib import Path

from promptlab.enums import TracerType
from promptlab.types import ExperimentConfig, TracerConfig

class ConfigValidator:

    @staticmethod
    def validate_tracer_config(tracer_config: TracerConfig):
        validate_db_type(tracer_config.type)
        validate_db_file_exists(tracer_config.db_file)

    @staticmethod
    def validate_experiment_config(experiment_config: ExperimentConfig):
        validate_prompt_template_id(experiment_config.prompt_template.id)
        validate_dataset_id(experiment_config.dataset.id)

def validate_db_type(db_type: str) -> None:

    valid_types = set(item.value for item in TracerType)
    
    if not isinstance(db_type, str):
        raise ValueError(f"Database type must be a string, got {type(db_type)}")
    
    if db_type not in valid_types:
        raise ValueError(f"Unsupported database type: {db_type}. Must be one of: {', '.join(valid_types)}")

def validate_db_file_exists(db_file: str) -> None:

    if not isinstance(db_file, str):
        raise ValueError(f"Database file path must be a string, got {type(db_file)}")
    
    try:
        path = Path(db_file)
        
        # Check if file exists
        if path.exists():
            if not path.is_file():
                raise ValueError(f"Path exists but is not a file: {db_file}")
            if not os.access(path, os.W_OK):
                raise ValueError(f"Database file exists but is not writable: {db_file}")
        else:
            # If file doesn't exist, check if parent directory exists and is writable
            parent_dir = path.parent
            if not parent_dir.exists():
                raise ValueError(f"Parent directory does not exist: {parent_dir}")
            if not os.access(parent_dir, os.W_OK):
                raise ValueError(f"Parent directory is not writable: {parent_dir}")
                
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Invalid database file path: {str(e)}")

def validate_prompt_template_id(template_path: str) -> None:

    if not isinstance(template_path, str):
        raise ValueError(f"Template path must be a string, got {type(template_path)}")

def validate_dataset_id(dataset_path: str) -> None:

    if not isinstance(dataset_path, str):
        raise ValueError(f"Dataset path must be a string, got {type(dataset_path)}")