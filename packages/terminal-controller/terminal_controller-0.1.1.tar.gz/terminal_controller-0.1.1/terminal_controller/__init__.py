"""Terminal Controller MCP Package."""

__version__ = "0.1.0"

# Import the main function to make it available at package level
from .main import main

# This makes the function available when someone imports the package
__all__ = ["main"]