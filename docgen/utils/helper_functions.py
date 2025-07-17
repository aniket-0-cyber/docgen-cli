"""
Helper functions module for various utility operations.

This module provides additional helper functions for common tasks
and can be used for testing GitHub webhook functionality.
"""

import json
import hashlib
import random
import string
from pathlib import Path
from typing import List, Dict, Union, Any


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length.
    
    Args:
        length (int): Length of the string to generate (default: 10)
        
    Returns:
        str: Random string containing letters and digits
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """Calculate SHA256 hash of a file.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        
    Returns:
        str: SHA256 hash of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def merge_dictionaries(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries recursively.
    
    Args:
        dict1 (Dict): First dictionary
        dict2 (Dict): Second dictionary
        
    Returns:
        Dict: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dictionaries(result[key], value)
        else:
            result[key] = value
    
    return result


def filter_list_by_criteria(items: List[Any], criteria: callable) -> List[Any]:
    """Filter a list based on a criteria function.
    
    Args:
        items (List[Any]): List of items to filter
        criteria (callable): Function that returns True for items to keep
        
    Returns:
        List[Any]: Filtered list
    """
    return [item for item in items if criteria(item)]


def create_directory_structure(base_path: Union[str, Path], structure: Dict) -> None:
    """Create directory structure from a nested dictionary.
    
    Args:
        base_path (Union[str, Path]): Base directory path
        structure (Dict): Nested dictionary representing directory structure
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    for name, content in structure.items():
        current_path = base_path / name
        if isinstance(content, dict):
            create_directory_structure(current_path, content)
        else:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, str):
                current_path.write_text(content)


def validate_json_string(json_string: str) -> bool:
    """Validate if a string is valid JSON.
    
    Args:
        json_string (str): String to validate
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size.
    
    Args:
        lst (List[Any]): List to chunk
        chunk_size (int): Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def find_common_elements(list1: List[Any], list2: List[Any]) -> List[Any]:
    """Find common elements between two lists.
    
    Args:
        list1 (List[Any]): First list
        list2 (List[Any]): Second list
        
    Returns:
        List[Any]: List of common elements
    """
    return list(set(list1) & set(list2))


# Test function for webhook validation
def webhook_validation_test():
    """Test function to validate webhook functionality."""
    test_data = {
        'random_id': generate_random_string(8),
        'test_status': 'active',
        'validation_passed': True,
        'sample_data': [1, 2, 3, 4, 5]
    }
    
    print(f"Webhook validation test executed with data: {test_data}")
    return test_data


if __name__ == "__main__":
    # Demo usage
    print("Helper functions module loaded!")
    print(f"Random string: {generate_random_string()}")
    print(f"Sample file size: {format_file_size(1024 * 1024)}")
    print(f"Webhook test: {webhook_validation_test()}") 