import os
import fnmatch
import psutil
import signal
from datetime import datetime
from pathlib import Path
import subprocess
from fastmcp import FastMCP


# Initialize the fast-mcp server
mcp = FastMCP("Local File System MCP Server")

    
@mcp.tool
def list_directory(path:str) -> list[str]:
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
def get_file_metadata(path: str) -> str:
    """
    Returns detailed metadata about a file or directory.
    
    Args:
        path: Path to the file or directory.
    
    Returns:
        A formatted string with file metadata including:
        - Type (file/directory)
        - Size (in bytes and human-readable format)
        - Permissions (in octal format)
        - Owner and group
        - Creation, modification, and access times
    
    Example:
        get_file_metadata("/home/user/document.txt") -> returns formatted metadata
    """
    try:
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        stat_info = os.stat(path)
        
        # Get file type
        file_type = "Directory" if os.path.isdir(path) else "File"
        
        # Get size
        size_bytes = stat_info.st_size
        if size_bytes < 1024:
            size_human = f"{size_bytes} bytes"
        elif size_bytes < 1024**2:
            size_human = f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024**3:
            size_human = f"{size_bytes/(1024**2):.2f} MB"
        else:
            size_human = f"{size_bytes/(1024**3):.2f} GB"
        
        # Get permissions
        permissions = oct(stat_info.st_mode)[-3:]
        
        # Get times
        created = datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed = datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        metadata = f"""
Type: {file_type}
Size: {size_human} ({size_bytes} bytes)
Permissions: {permissions}
Owner UID: {stat_info.st_uid}
Group GID: {stat_info.st_gid}
Created: {created}
Modified: {modified}
Accessed: {accessed}
"""
        return metadata.strip()
    except PermissionError:
        return f"Error: Permission denied for '{path}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_disk_usage(path: str) -> str:
    """
    Returns disk space usage information for a given path.
    
    Args:
        path: Directory path to check disk usage for.
    
    Returns:
        A formatted string with total, used, and available disk space in human-readable format.
    
    Example:
        get_disk_usage("/home") -> "Total: 500 GB, Used: 300 GB (60%), Free: 200 GB (40%)"
    """
    try:
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        usage = psutil.disk_usage(path)
        
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        
        result = f"""
Total: {total_gb:.2f} GB
Used: {used_gb:.2f} GB ({usage.percent}%)
Free: {free_gb:.2f} GB ({100 - usage.percent:.1f}%)
"""
        return result.strip()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def find_large_files(directory: str, min_size_mb: int = 100) -> str:
    """
    Finds all files larger than the specified size in a directory (recursively).
    
    Args:
        directory: Directory path to search in.
        min_size_mb: Minimum file size in megabytes (default: 100 MB).
    
    Returns:
        A formatted string listing large files with their paths and sizes, sorted by size (largest first).
    
    Example:
        find_large_files("/home/user", 50) -> lists all files > 50MB
    """
    try:
        if not os.path.isdir(directory):
            return f"Error: Directory '{directory}' does not exist."
        
        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    if size >= min_size_bytes:
                        size_mb = size / (1024**2)
                        large_files.append((filepath, size_mb))
                except (OSError, PermissionError):
                    continue
        
        if not large_files:
            return f"No files larger than {min_size_mb} MB found in '{directory}'."
        
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        result = f"Files larger than {min_size_mb} MB in '{directory}':\n\n"
        for filepath, size_mb in large_files:
            result += f"{size_mb:.2f} MB - {filepath}\n"
        
        return result.strip()
    except PermissionError:
        return f"Error: Permission denied for directory '{directory}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def list_processes() -> str:
    """
    Lists all currently running processes on the system.
    
    Returns:
        A formatted string with process information including PID, name, CPU%, memory%, 
        and status for all running processes, sorted by CPU usage (highest first).
    
    Example:
        list_processes() -> returns formatted list of all processes
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': pinfo['cpu_percent'] or 0.0,
                    'memory': pinfo['memory_percent'] or 0.0,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        
        result = f"{'PID':<8} {'Name':<30} {'CPU%':<8} {'Memory%':<10} {'Status':<10}\n"
        result += "-" * 76 + "\n"
        
        for proc in processes[:50]:  # Limit to top 50 processes
            result += f"{proc['pid']:<8} {proc['name'][:29]:<30} {proc['cpu']:<8.1f} {proc['memory']:<10.2f} {proc['status']:<10}\n"
        
        if len(processes) > 50:
            result += f"\n... and {len(processes) - 50} more processes"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_process_info(pid: int) -> str:
    """
    Returns detailed information about a specific process.
    
    Args:
        pid: Process ID to get information about.
    
    Returns:
        A formatted string with detailed process information including name, status, 
        CPU usage, memory usage, command line, creation time, and more.
    
    Example:
        get_process_info(1234) -> returns detailed info for process 1234
    """
    try:
        proc = psutil.Process(pid)
        
        # Get process info
        with proc.oneshot():
            name = proc.name()
            status = proc.status()
            cpu_percent = proc.cpu_percent(interval=0.1)
            memory_info = proc.memory_info()
            memory_percent = proc.memory_percent()
            create_time = datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                cmdline = ' '.join(proc.cmdline())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cmdline = "Access denied"
            
            try:
                cwd = proc.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cwd = "Access denied"
            
            try:
                username = proc.username()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                username = "Access denied"
        
        result = f"""
Process ID: {pid}
Name: {name}
Status: {status}
User: {username}
CPU Usage: {cpu_percent}%
Memory Usage: {memory_percent:.2f}% ({memory_info.rss / (1024**2):.2f} MB)
Created: {create_time}
Working Directory: {cwd}
Command Line: {cmdline}
"""
        return result.strip()
    except psutil.NoSuchProcess:
        return f"Error: No process with PID {pid} found."
    except psutil.AccessDenied:
        return f"Error: Access denied for process {pid}."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def kill_process(pid: int, signal_name: str = "SIGTERM") -> str:
    """
    Terminates a process by sending it a signal.
    
    Args:
        pid: Process ID to terminate.
        signal_name: Signal to send (default: "SIGTERM" for graceful termination).
                    Options: "SIGTERM" (graceful), "SIGKILL" (force), "SIGINT" (interrupt).
    
    Returns:
        Success or error message.
    
    WARNING: This will terminate the specified process. Use with caution!
    
    Example:
        kill_process(1234, "SIGTERM") -> attempts graceful termination of process 1234
    """
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        # Map signal names to signal values
        signal_map = {
            "SIGTERM": signal.SIGTERM,
            "SIGKILL": signal.SIGKILL,
            "SIGINT": signal.SIGINT
        }
        
        if signal_name not in signal_map:
            return f"Error: Invalid signal '{signal_name}'. Valid options: SIGTERM, SIGKILL, SIGINT"
        
        sig = signal_map[signal_name]
        proc.send_signal(sig)
        
        return f"Successfully sent {signal_name} to process {pid} ({proc_name})."
    except psutil.NoSuchProcess:
        return f"Error: No process with PID {pid} found."
    except psutil.AccessDenied:
        return f"Error: Permission denied. Cannot kill process {pid}. May require root/admin privileges."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_system_stats() -> str:
    """
    Returns overall system statistics including CPU, memory, swap, and uptime.
    
    Returns:
        A formatted string with comprehensive system statistics.
    
    Example:
        get_system_stats() -> returns current system resource usage
    """
    try:
        # CPU stats
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        
        # Memory stats
        memory = psutil.virtual_memory()
        
        # Swap stats
        swap = psutil.swap_memory()
        
        # Boot time / uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        uptime_seconds = datetime.now().timestamp() - psutil.boot_time()
        uptime_str = str(datetime.fromtimestamp(uptime_seconds).strftime('%d days, %H:%M:%S'))
        
        result = f"""
=== CPU ===
Usage: {cpu_percent}%
Physical Cores: {cpu_count_physical}
Logical Cores: {cpu_count}

=== Memory ===
Total: {memory.total / (1024**3):.2f} GB
Used: {memory.used / (1024**3):.2f} GB ({memory.percent}%)
Available: {memory.available / (1024**3):.2f} GB

=== Swap ===
Total: {swap.total / (1024**3):.2f} GB
Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)
Free: {swap.free / (1024**3):.2f} GB

=== System ===
Boot Time: {boot_time}
Uptime: {uptime_str}
"""
        return result.strip()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_network_connections() -> str:
    """
    Lists all active network connections on the system.
    
    Returns:
        A formatted string showing active network connections with protocol, 
        local address, remote address, status, and associated process.
    
    Example:
        get_network_connections() -> returns list of all network connections
    """
    try:
        connections = psutil.net_connections(kind='inet')
        
        result = f"{'Protocol':<10} {'Local Address':<25} {'Remote Address':<25} {'Status':<15} {'PID':<8}\n"
        result += "-" * 93 + "\n"
        
        for conn in connections[:100]:  # Limit to 100 connections
            protocol = "TCP" if conn.type == 1 else "UDP"
            local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
            remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            status = conn.status if conn.status else "N/A"
            pid = str(conn.pid) if conn.pid else "N/A"
            
            result += f"{protocol:<10} {local_addr:<25} {remote_addr:<25} {status:<15} {pid:<8}\n"
        
        if len(connections) > 100:
            result += f"\n... and {len(connections) - 100} more connections"
        
        return result
    except psutil.AccessDenied:
        return "Error: Permission denied. Network connections require root/admin privileges."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_logged_in_users() -> str:
    """
    Lists all currently logged in users on the system.
    
    Returns:
        A formatted string with information about logged in users including 
        username, terminal, host, and login time.
    
    Example:
        get_logged_in_users() -> returns list of logged in users
    """
    try:
        users = psutil.users()
        
        if not users:
            return "No users currently logged in."
        
        result = f"{'User':<15} {'Terminal':<12} {'Host':<20} {'Login Time':<20}\n"
        result += "-" * 67 + "\n"
        
        for user in users:
            login_time = datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
            host = user.host if user.host else "localhost"
            result += f"{user.name:<15} {user.terminal:<12} {host:<20} {login_time:<20}\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def read_log_tail(log_path: str, lines: int = 50) -> str:
    """
    Reads the last N lines from a log file.
    
    Args:
        log_path: Path to the log file to read.
        lines: Number of lines to read from the end (default: 50).
    
    Returns:
        The last N lines of the log file.
    
    Example:
        read_log_tail("/var/log/syslog", 20) -> returns last 20 lines of syslog
    """
    try:
        if not os.path.isfile(log_path):
            return f"Error: Log file '{log_path}' not found."
        
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return ''.join(last_lines)
    except PermissionError:
        return f"Error: Permission denied for log file '{log_path}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def search_logs(log_path: str, pattern: str, max_results: int = 100) -> str:
    """
    Searches for lines matching a pattern in a log file.
    
    Args:
        log_path: Path to the log file to search.
        pattern: Text pattern to search for (case-insensitive).
        max_results: Maximum number of matching lines to return (default: 100).
    
    Returns:
        All lines containing the search pattern, limited to max_results.
    
    Example:
        search_logs("/var/log/syslog", "error") -> returns lines containing "error"
    """
    try:
        if not os.path.isfile(log_path):
            return f"Error: Log file '{log_path}' not found."
        
        matches = []
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if pattern.lower() in line.lower():
                    matches.append(f"Line {line_num}: {line.rstrip()}")
                    if len(matches) >= max_results:
                        break
        
        if not matches:
            return f"No matches found for pattern '{pattern}' in '{log_path}'."
        
        result = f"Found {len(matches)} matches for '{pattern}' in '{log_path}':\n\n"
        result += '\n'.join(matches)
        
        return result
    except PermissionError:
        return f"Error: Permission denied for log file '{log_path}'."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def list_systemd_services() -> str:
    """
    Lists all systemd services and their current status (Linux only).
    
    Returns:
        A formatted string with service names, load state, active state, and description.
        Shows both running and stopped services.
    
    Note: This tool only works on Linux systems with systemd.
    
    Example:
        list_systemd_services() -> returns list of all systemd services
    """
    try:
        result = subprocess.run(
            ['systemctl', 'list-units', '--type=service', '--all', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"Error: Failed to list services. {result.stderr}"
        
        return result.stdout
    except FileNotFoundError:
        return "Error: systemctl command not found. This tool only works on Linux systems with systemd."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_service_status(service_name: str) -> str:
    """
    Gets the status of a specific systemd service (Linux only).
    
    Args:
        service_name: Name of the systemd service (e.g., 'nginx', 'ssh', 'apache2').
    
    Returns:
        Detailed status information about the service including whether it's running,
        enabled, recent logs, and service description.
    
    Example:
        get_service_status("nginx") -> returns status of nginx service
    """
    try:
        result = subprocess.run(
            ['systemctl', 'status', service_name, '--no-pager'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # systemctl status returns 0 for active, 3 for inactive, 4 for not found
        if result.returncode == 4:
            return f"Error: Service '{service_name}' not found."
        
        return result.stdout
    except FileNotFoundError:
        return "Error: systemctl command not found. This tool only works on Linux systems with systemd."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def check_port_listening(port: int) -> str:
    """
    Checks if a specific port is in use and which process is using it.
    
    Args:
        port: Port number to check (e.g., 80, 443, 3000, 8080).
    
    Returns:
        Information about whether the port is in use, and if so, which process 
        is using it (PID, name, and command).
    
    Example:
        check_port_listening(80) -> checks if port 80 is in use
    """
    try:
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.laddr and conn.laddr.port == port:
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        proc_name = proc.name()
                        proc_cmdline = ' '.join(proc.cmdline())
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "Unknown"
                        proc_cmdline = "Access denied"
                else:
                    proc_name = "Unknown"
                    proc_cmdline = "No PID available"
                
                status = conn.status if conn.status else "N/A"
                protocol = "TCP" if conn.type == 1 else "UDP"
                
                result = f"""
Port {port} is IN USE

Protocol: {protocol}
Status: {status}
Process ID: {conn.pid if conn.pid else 'N/A'}
Process Name: {proc_name}
Command: {proc_cmdline}
Local Address: {conn.laddr.ip}:{conn.laddr.port}
"""
                return result.strip()
        
        return f"Port {port} is NOT in use (available)."
    except psutil.AccessDenied:
        return "Error: Permission denied. Checking ports may require root/admin privileges."
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print("Starting MCP server on http://localhost:9000...")
    mcp.run(transport="http",
            host="localhost",         
            port=9000,  
            )