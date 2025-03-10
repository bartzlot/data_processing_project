import json
import os

def load_config(file_path="config.json") -> dict:
    """Load a JSON config file and return as a dictionary."""

    config_path = os.path.join(os.path.dirname(__file__), '..', 'info_data', file_path)

    try:
        
        with open(config_path, "r") as file:
            config = json.load(file)
        return config
    
    except FileNotFoundError:
        print("Error: Config file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return {}