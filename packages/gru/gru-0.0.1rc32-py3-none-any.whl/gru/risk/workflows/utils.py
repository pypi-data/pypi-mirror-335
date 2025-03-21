import json
from pathlib import Path
from typing import Dict, Any

def read_json_config(file_path: str) -> Dict[str, Any]:
    """
    Read and validate JSON configuration file.
    
    Args:
        file_path: Path to JSON config file
        
    Returns:
        Dict containing parsed JSON data
        
    Raises:
        ValueError: If file doesn't exist or isn't valid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Config file not found: {file_path}")
        
    try:
        with path.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {str(e)}")