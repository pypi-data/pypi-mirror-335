"""
Contains utility functions
"""

def load_api_key(name: str) -> str:
    """
    Loads the API key from the file
    """
    with open(f"../secret/{name}.txt", "r", encoding='utf-8') as f:
        return f.read().strip()
