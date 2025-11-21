import os
import fnmatch
import subprocess
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastmcp import FastMCP


# Initialize the fast-mcp server
mcp = FastMCP("Local File System MCP Server")

    
@mcp.tool
def list_directory(path: str) -> list[str]:
    """
    Lists all files and subdirectories in a specified directory path.
    Only lists the contents one level deep.
    """
    try:
        if not os.path.isdir(path):
            return [f"Error: Path '{path}' is not a valid directory."]
        
        contents = os.listdir(path)
        if not contents:
            return ["Directory is empty."]
        return contents
    except PermissionError:
        return [f"Error: Permission denied for directory '{path}'."]
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool
def get_file_content(path: str) -> str:
    """
    Reads and returns the content of a specified text file.
    
    Args:
        path: Absolute or relative path to the text file to read.
    
    Returns:
        The content of the file as a string, or an error message if the file 
        cannot be read (e.g., doesn't exist, no permissions, binary file).
    
    Example:
        get_file_content("/etc/hosts") -> returns the hosts file content
    """
    try:
        if not os.path.isfile(path):
            return f"Error: File not found at '{path}'."

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except PermissionError:
        return f"Error: Permission denied for file '{path}'."
    except UnicodeDecodeError:
        return f"Error: Cannot decode file. It might be a binary file, not text."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def search_files(directory: str, pattern: str) -> list[str]:
    """
    Recursively searches for files matching a pattern in the specified directory.
    
    Args:
        directory: The directory path to search in.
        pattern: The file pattern to match (e.g., '*.py', 'config.*', '*.txt').
                Uses glob-style wildcards: * matches anything, ? matches single character.
    
    Returns:
        A list of absolute paths to files matching the pattern. Returns error message if 
        directory doesn't exist or permission denied.
    
    Example:
        search_files("/home/user", "*.py") -> ["/home/user/script.py", "/home/user/src/app.py"]
    """
    try:
        if not os.path.isdir(directory):
            return [f"Error: Directory '{directory}' does not exist."]
        
        matches = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(root, filename))
        
        if not matches:
            return [f"No files matching pattern '{pattern}' found in '{directory}'."]
        
        return matches
    except PermissionError:
        return [f"Error: Permission denied for directory '{directory}'."]
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool
def write_file(path: str, content: str) -> str:
    """
    Writes content to a file. Creates the file if it doesn't exist, or overwrites it if it does.
    
    Args:
        path: Absolute or relative path to the file to write.
        content: The text content to write to the file.
    
    Returns:
        Success message or error message if the operation fails.
    
    Example:
        write_file("/tmp/test.txt", "Hello World") -> "Successfully wrote 11 bytes to '/tmp/test.txt'."
    """
    try:
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        with open(path, 'w', encoding='utf-8') as f:
            bytes_written = f.write(content)
        
        return f"Successfully wrote {bytes_written} bytes to '{path}'."
    except PermissionError:
        return f"Error: Permission denied for file '{path}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def execute_command(command: str, timeout: int = 30, confirmed: bool = False) -> str:
    """
    Executes a shell command and returns its output.
    
    Args:
        command: The shell command to execute.
        timeout: Maximum seconds to wait for command completion (default: 30).
        confirmed: Must be set to True after user confirmation (default: False).
    
    Returns:
        The command's stdout and stderr output, or an error message.
    
    Warning:
        ALL commands require user confirmation before execution for safety.
    
    Example:
        execute_command("ls -la /tmp") -> asks for confirmation first
        execute_command("ls -la /tmp", confirmed=True) -> executes after user approval
    """
    # Require confirmation for ALL commands
    if not confirmed:
        return (f"⚠️  CONFIRMATION REQUIRED ⚠️\n\n"
                f"Command to execute:\n"
                f"  '{command}'\n\n"
                f"The agent must ask you for permission before running this command.\n"
                f"If you approve, the agent will call this tool again with confirmed=True.")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        
        if result.returncode != 0:
            output += f"\n[Exit Code: {result.returncode}]"
        
        return output if output else "[No output]"
    
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error: {str(e)}"


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = mcp.http_app(middleware=middleware)