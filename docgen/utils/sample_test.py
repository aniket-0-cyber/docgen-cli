"""
Sample utility module for testing purposes.

This module contains simple utility functions that can be used
for testing GitHub webhooks and other functionality.
"""

import os
import datetime
from typing import Optional, Dict, Any


def get_current_timestamp() -> str:
    """Get the current timestamp as a formatted string.
    
    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.datetime.now().isoformat()


def get_environment_info() -> Dict[str, Any]:
    """Get basic environment information.
    
    Returns:
        Dict[str, Any]: Dictionary containing environment details
    """
    return {
        'python_version': os.sys.version,
        'platform': os.name,
        'current_working_directory': os.getcwd(),
        'timestamp': get_current_timestamp(),
        'environment_variables_count': len(os.environ)
    }


def validate_file_path(file_path: str) -> bool:
    """Validate if a file path exists.
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.exists(file_path)


def create_simple_log_entry(message: str, level: str = "INFO") -> Dict[str, str]:
    """Create a simple log entry.
    
    Args:
        message (str): Log message
        level (str): Log level (default: "INFO")
        
    Returns:
        Dict[str, str]: Log entry dictionary
    """
    return {
        'timestamp': get_current_timestamp(),
        'level': level,
        'message': message
    }


def calculate_simple_stats(numbers: list) -> Optional[Dict[str, float]]:
    """Calculate basic statistics for a list of numbers.
    
    Args:
        numbers (list): List of numeric values
        
    Returns:
        Optional[Dict[str, float]]: Statistics dictionary or None if empty list
    """
    if not numbers:
        return None
        
    return {
        'count': len(numbers),
        'sum': sum(numbers),
        'average': sum(numbers) / len(numbers),
        'min': min(numbers),
        'max': max(numbers)
    }


# Test function for webhook verification
def webhook_test_function():
    """Simple function to test webhook triggers."""
    print("Webhook test function executed!")
    return {
        'status': 'success',
        'message': 'Webhook test completed',
        'timestamp': get_current_timestamp()
    }


if __name__ == "__main__":
    # Simple test when run directly
    print("Sample test module loaded successfully!")
    print(f"Environment info: {get_environment_info()}")
    print(f"Webhook test: {webhook_test_function()}") 