# Terminal Controller for MCP

A Model Context Protocol (MCP) server that enables secure terminal command execution, directory navigation, and file system operations through a standardized interface.

![](https://badge.mcpx.dev?type=server 'MCP Server')

## Features

- **Command Execution**: Run terminal commands with timeout controls and comprehensive output capture
- **Directory Management**: Navigate and list directory contents with intuitive formatting
- **Security Measures**: Built-in safeguards against dangerous commands and operations
- **Command History**: Track and display recent command executions
- **Cross-Platform Support**: Works on both Windows and UNIX-based systems

## How It Works

Terminal Controller implements the Model Context Protocol (MCP) to provide a secure interface between LLMs and your terminal. It exposes several tools that allow models to:

1. Execute terminal commands with proper error handling and timeout controls
2. Navigate through directories while maintaining proper access controls
3. List contents of directories with clear visual formatting
4. Track command history for reference and auditing

## Installation

### Prerequisites

- Python 3.10+
- MCP-compatible client (such as Claude Desktop)

### Automated Setup (Recommended)

The easiest way to set up Terminal Controller is using the provided setup script:

1. Clone this repository:
   ```bash
   git clone https://github.com/GongRzhe/terminal-controller-mcp.git
   cd terminal-controller-mcp
   ```

2. Run the setup script:
   ```bash
   python setup_mcp.py
   ```

This script will:
- Create a Python virtual environment (`.venv`) if it doesn't exist
- Install all required dependencies from `requirements.txt`
- Generate the MCP configuration file with correct paths
- Display configuration instructions for various MCP clients

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Clone this repository:
   ```bash
   git clone https://github.com/GongRzhe/terminal-controller-mcp.git
   cd terminal-controller-mcp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your MCP client to use the server. For Claude Desktop, add this to your `claude_desktop_config.json`:
   ```json
   "terminal-controller": {
     "command": "/path/to/terminal-controller/.venv/bin/python", # "/path/to/terminal-controller/.venv/Scripts/python"
     "args": [
       "/path/to/terminal-controller/terminal_controller.py"
     ],
     "env": {
       "PYTHONPATH": "/path/to/terminal-controller"
     }
   }
   ```

## Client Configuration

### Claude Desktop

The configuration path varies by operating system:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Cursor

For Cursor, use the path displayed after running the setup script.

### Other MCP Clients

For other clients, refer to their documentation on how to configure external MCP servers.

## Usage

Once configured, you can use natural language to interact with your terminal through your MCP client:

- "Run the command `ls -la` in the current directory"
- "Navigate to my Documents folder"
- "Show me the contents of my Downloads directory"
- "Show me my recent command history"

## API Reference

Terminal Controller exposes the following MCP tools:

### `execute_command`

Execute a terminal command and return its results.

**Parameters:**
- `command`: The command line command to execute
- `timeout`: Command timeout in seconds (default: 30)

**Returns:**
- Output of the command execution, including stdout, stderr, and execution status

### `get_command_history`

Get recent command execution history.

**Parameters:**
- `count`: Number of recent commands to return (default: 10)

**Returns:**
- Formatted command history record

### `get_current_directory`

Get the current working directory.

**Returns:**
- Path of current working directory

### `change_directory`

Change the current working directory.

**Parameters:**
- `path`: Directory path to switch to

**Returns:**
- Operation result information

### `list_directory`

List files and subdirectories in the specified directory.

**Parameters:**
- `path`: Directory path to list contents (default: current directory)

**Returns:**
- List of directory contents, formatted with icons for directories and files

## Security Considerations

Terminal Controller implements several security measures:

- Timeout controls to prevent long-running commands
- Blacklisting of dangerous commands (rm -rf /, format, mkfs)
- Proper error handling and isolation of command execution
- Access only to the commands and directories specifically granted

## Limitations

- Only commands that complete within the timeout period will return results
- By default, the server has access to the same file system permissions as the user running it
- Some interactive commands may not work as expected due to the non-interactive nature of the terminal interface

## Troubleshooting

If you encounter issues:

1. Check that your Python version is 3.10 or higher
2. Verify that the paths in your configuration file are correct and absolute
3. Make sure the virtual environment is properly activated when installing dependencies
4. Review your MCP client's logs for connection errors

## License

MIT
