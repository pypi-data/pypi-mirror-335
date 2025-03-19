import asyncio
import os
import subprocess
import platform
from typing import List, Dict, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("terminal-controller")

# List to store command history
command_history = []

# Maximum history size
MAX_HISTORY_SIZE = 50

async def run_command(cmd: str, timeout: int = 30) -> Dict:
    """
    Execute command and return results
    
    Args:
        cmd: Command to execute
        timeout: Command timeout in seconds
        
    Returns:
        Dictionary containing command execution results
    """
    start_time = datetime.now()
    
    try:
        # Create command appropriate for current OS
        if platform.system() == "Windows":
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
        else:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True,
                executable="/bin/bash"
            )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
            stdout = stdout.decode('utf-8', errors='replace')
            stderr = stderr.decode('utf-8', errors='replace')
            return_code = process.returncode
        except asyncio.TimeoutError:
            try:
                process.kill()
            except:
                pass
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "return_code": -1,
                "duration": str(datetime.now() - start_time),
                "command": cmd
            }
    
        duration = datetime.now() - start_time
        result = {
            "success": return_code == 0,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "duration": str(duration),
            "command": cmd
        }
        
        # Add to history
        command_history.append({
            "timestamp": datetime.now().isoformat(),
            "command": cmd,
            "success": return_code == 0
        })
        
        # If history is too long, remove oldest record
        if len(command_history) > MAX_HISTORY_SIZE:
            command_history.pop(0)
            
        return result
    
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "return_code": -1,
            "duration": str(datetime.now() - start_time),
            "command": cmd
        }

@mcp.tool()
async def execute_command(command: str, timeout: int = 30) -> str:
    """
    Execute terminal command and return results
    
    Args:
        command: Command line command to execute
        timeout: Command timeout in seconds, default is 30 seconds
    
    Returns:
        Output of the command execution
    """
    # Check for dangerous commands (can add more security checks)
    dangerous_commands = ["rm -rf /",  "mkfs"]
    if any(dc in command.lower() for dc in dangerous_commands):
        return "For security reasons, this command is not allowed."
    
    result = await run_command(command, timeout)
    
    if result["success"]:
        output = f"Command executed successfully (duration: {result['duration']})\n\n"
        
        if result["stdout"]:
            output += f"Output:\n{result['stdout']}\n"
        else:
            output += "Command had no output.\n"
            
        if result["stderr"]:
            output += f"\nWarnings/Info:\n{result['stderr']}"
            
        return output
    else:
        output = f"Command execution failed (duration: {result['duration']})\n"
        
        if result["stdout"]:
            output += f"\nOutput:\n{result['stdout']}\n"
            
        if result["stderr"]:
            output += f"\nError:\n{result['stderr']}"
            
        output += f"\nReturn code: {result['return_code']}"
        return output

@mcp.tool()
async def get_command_history(count: int = 10) -> str:
    """
    Get recent command execution history
    
    Args:
        count: Number of recent commands to return
    
    Returns:
        Formatted command history record
    """
    if not command_history:
        return "No command execution history."
    
    count = min(count, len(command_history))
    recent_commands = command_history[-count:]
    
    output = f"Recent {count} command history:\n\n"
    
    for i, cmd in enumerate(recent_commands):
        status = "✓" if cmd["success"] else "✗"
        output += f"{i+1}. [{status}] {cmd['timestamp']}: {cmd['command']}\n"
    
    return output

@mcp.tool()
async def get_current_directory() -> str:
    """
    Get current working directory
    
    Returns:
        Path of current working directory
    """
    return os.getcwd()

@mcp.tool()
async def change_directory(path: str) -> str:
    """
    Change current working directory
    
    Args:
        path: Directory path to switch to
    
    Returns:
        Operation result information
    """
    try:
        os.chdir(path)
        return f"Switched to directory: {os.getcwd()}"
    except FileNotFoundError:
        return f"Error: Directory '{path}' does not exist"
    except PermissionError:
        return f"Error: No permission to access directory '{path}'"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

@mcp.tool()
async def list_directory(path: Optional[str] = None) -> str:
    """
    List files and subdirectories in the specified directory
    
    Args:
        path: Directory path to list contents, default is current directory
    
    Returns:
        List of directory contents
    """
    if path is None:
        path = os.getcwd()
    
    try:
        items = os.listdir(path)
        
        dirs = []
        files = []
        
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                dirs.append(f"📁 {item}/")
            else:
                files.append(f"📄 {item}")
        
        # Sort directories and files
        dirs.sort()
        files.sort()
        
        if not dirs and not files:
            return f"Directory '{path}' is empty"
        
        output = f"Contents of directory '{path}':\n\n"
        
        if dirs:
            output += "Directories:\n"
            output += "\n".join(dirs) + "\n\n"
        
        if files:
            output += "Files:\n"
            output += "\n".join(files)
        
        return output
    
    except FileNotFoundError:
        return f"Error: Directory '{path}' does not exist"
    except PermissionError:
        return f"Error: No permission to access directory '{path}'"
    except Exception as e:
        return f"Error listing directory contents: {str(e)}"

def main():
    """
    Entry point for the terminal-controller command.
    This function is called when the package is run as a script.
    """
    # Initialize and run server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Initialize and run server when script is executed directly
    main()