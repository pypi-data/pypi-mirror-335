from typing import Any


def load_deployment_wise_queues(json_path: str) -> dict[str, dict[str, Any]]:
    """
    Loads worker queue statistics from a JSON file and returns deployment-wise queue statistics.

    Args:
        json_path (str): Path to the JSON file containing worker queue statistics.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where keys are deployment names and values are dictionaries
        containing 'total_queues' and 'queue_details'.

    Raises:
        ValueError: If the input is not a valid JSON file.
        FileNotFoundError: If the specified JSON file does not exist.
    """
    import json

    try:
        with open(json_path) as file:
            worker_queue_json = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found at path: {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in file: {json_path}. Error: {e}")

    if not isinstance(worker_queue_json, dict):
        raise ValueError("Expected a dictionary from the JSON file.")

    deployment_wise_queues = {}

    for deployment, queues in worker_queue_json.items():
        if not isinstance(queues, list):
            raise ValueError(f"Expected a list of queues for deployment: {deployment}")
        deployment_wise_queues[deployment] = {"total_queues": len(queues), "queue_details": queues}

    return deployment_wise_queues


def load_organization_metadata(json_path: str) -> dict[str, Any]:
    """
    Loads deployment configuration from a JSON file.

    Args:
        json_path (str): Path to the JSON file containing deployment configuration.

    Returns:
        Dict[str, Any]: A dictionary containing deployment configurations.

    Raises:
        ValueError: If the input is not a valid JSON file.
        FileNotFoundError: If the specified JSON file does not exist.
    """
    import json

    try:
        with open(json_path) as file:
            deployment_config = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found at path: {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in file: {json_path}. Error: {e}")

    if not isinstance(deployment_config, dict):
        raise ValueError("Expected a dictionary from the JSON file.")

    return deployment_config
