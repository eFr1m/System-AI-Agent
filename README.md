# System Administration AI Agent with MCP

A system administration agent powered by AI that can interact with the local file system through the Model Context Protocol (MCP). The agent uses a local LLM (Ollama) to understand natural language commands and execute file system operations safely.

## Overview

This project consists of three main components:

- **MCP Server**: Exposes file system operations as tools via the Model Context Protocol
- **AI Agent**: Processes natural language requests and calls MCP tools to fulfill them
- **Local LLM**: Ollama running Qwen 3:14b model for language understanding

## Technologies Used

- **[Ollama](https://ollama.com/)**: Local LLM runtime (running Qwen3:14b model)
- **[Google ADK](https://github.com/google/generative-ai-python)**: Agent Development Kit for building AI agents
- **[FastMCP](https://github.com/jlowin/fastmcp)**: Framework for creating MCP servers
- **[LiteLLM](https://github.com/BerriAI/litellm)**: Unified interface for multiple LLM providers
- **Python 3.13+**: Programming language

## Installation

### 1. Install Ollama

```bash
# On Linux
curl -fsSL https://ollama.com/install.sh | sh

# On macOS
brew install ollama

# On Windows
# Download from https://ollama.com/download
```

### 2. Download the LLM Model

```bash
ollama pull qwen3:14b
```

### 3. Clone and Setup the Project

```bash
# Navigate to project directory
cd /path/to/project

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `system_agent/` directory:

```bash
echo 'OLLAMA_API_BASE="http://localhost:11434"' > system_agent/.env
```

Or export the variable in your shell:

```bash
export OLLAMA_API_BASE="http://localhost:11434"
```

## Usage

### Starting the System

The system requires two terminal windows running simultaneously.

#### Terminal 1: Start the MCP Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the MCP server
python src/mcp_server.py
```

You should see output indicating the server is running on `http://localhost:9000`.

#### Terminal 2: Start the AI Agent

```bash
# Activate virtual environment
source .venv/bin/activate

# Ensure Ollama is running (if not started automatically)
# ollama serve  # Run in another terminal if needed

# Start the agent
adk web
```

This will open a web browser with a chat interface where you can interact with the agent.

### Example Commands

Once the agent is running, you can interact with it using natural language:

```
User: List the contents of /home/user/Documents
Agent: [Lists all files and directories in the specified path]

User: Show me the content of /home/user/Documents/notes.txt
Agent: [Displays the file content]

User: Find all Python files in /home/user/projects
Agent: [Searches recursively and lists all .py files]

User: Create a file called test.txt with "Hello World"
Agent: [Creates the file with the specified content]

User: Run the command "df -h" to check disk space
Agent: [Asks for confirmation, then executes after approval]
```

## Available MCP Tools

- The MCP server exposes the following tools to the agent:

### 1. `list_directory(path: str) -> list[str]`

- Lists all files and subdirectories in the specified directory path (one level deep).

### 2. `get_file_content(path: str) -> str`

- Reads and returns the content of a text file.

### 3. `search_files(directory: str, pattern: str) -> list[str]`

- Recursively searches for files matching a glob pattern in the specified directory.
- Supports wildcards: `*` (anything), `?` (single character)

### 4. `write_file(path: str, content: str) -> str`

- Creates or overwrites a file with the specified content.

### 5. `execute_command(command: str, timeout: int = 30, confirmed: bool = False) -> str`

- Executes shell commands and returns their output.

- Confirmation workflow:
  1. Agent calls tool without confirmation
  2. Tool returns confirmation request
  3. Agent asks user for permission
  4. If approved, agent calls again with `confirmed=True`
