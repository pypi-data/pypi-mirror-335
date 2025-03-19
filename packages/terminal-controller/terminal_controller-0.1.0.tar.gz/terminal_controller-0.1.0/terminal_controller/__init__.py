"""Terminal Controller MCP Package.

A Model Context Protocol (MCP) server that enables secure terminal command 
execution, directory navigation, and file system operations through a 
standardized interface.
"""

__version__ = "0.1.0"

# When using the package structure, import from the main module
try:
    from .main import (
        execute_command,
        get_command_history,
        get_current_directory,
        change_directory,
        list_directory,
    )

    __all__ = [
        "execute_command",
        "get_command_history", 
        "get_current_directory", 
        "change_directory", 
        "list_directory"
    ]
except ImportError:
    # For single-file usage, this will fail but is handled
    pass