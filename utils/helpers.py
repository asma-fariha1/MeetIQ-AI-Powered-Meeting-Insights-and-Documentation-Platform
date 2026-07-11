# utils/helpers.py
# Helper utility functions for the AI Meeting Assistant.

def format_timestamp(seconds: float) -> str:
    """
    Formats duration in seconds to a string (e.g., HH:MM:SS).
    """
    # TODO: Implement formatting logic
    pass

def ensure_directory_exists(directory_path: str) -> None:
    """
    Creates a directory if it does not already exist.
    """
    import os
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
