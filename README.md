# System Administration AI Agent with MCP

A system administration agent powered by AI that can interact with the local file system through the Model Context Protocol (MCP). The agent uses a local LLM (Ollama) to understand natural language commands and execute file system operations safely.

## Overview

This project consists of three main components:

- **MCP Server**: Exposes file system operations as tools via the Model Context Protocol
- **AI Agent**: Processes natural language requests and calls MCP tools to fulfill them
- **Local LLM**: Ollama running Qwen 3:4b model for language understanding

## Technologies Used

- **[Ollama](https://ollama.com/)**: Local LLM runtime (running Qwen 3:4b model)
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
ollama pull qwen3:4b
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
python system_agent/agent.py
```

### Example Commands

Once the agent is running, you can interact with it using natural language:

```
User: List the contents of /home/user/Documents
Agent: [Lists all files and directories in the specified path]

User: Show me the content of /home/user/Documents/notes.txt
Agent: [Displays the file content]

User: What files are in the current directory?
Agent: [Lists files in the working directory]
```

## Available MCP Tools

The MCP server exposes the following tools to the agent:

### `list_directory(path: str) -> list[str]`

Lists all files and subdirectories in the specified directory path (one level deep).

**Features:**

- Validates directory existence
- Handles permission errors gracefully
- Reports empty directories

### `get_file_content(path: str) -> str`

Reads and returns the content of a text file.

**Features:**

- Validates file existence
- UTF-8 encoding support
- Detects and reports binary files
- Handles permission errors

## Project Structure

```
project/
├── .venv/                  # Virtual environment
├── requirements.txt        # Python dependencies
├── src/
│   └── mcp_server.py      # MCP server implementation
├── system_agent/
│   ├── __init__.py
│   ├── agent.py           # AI agent implementation
│   └── .env               # Environment variables
└── README.md              # This file
```

## Troubleshooting

### "Command 'python' not found"

Use `python3` instead of `python` on most Linux distributions.

### "ModuleNotFoundError"

Ensure the virtual environment is activated. You should see `(.venv)` in your terminal prompt.

### "Client failed to connect"

Make sure the MCP server is running in a separate terminal before starting the agent.

### "OLLAMA_API_BASE not found"

Set the environment variable either in `.env` file or export it in your shell session.

### Ollama connection issues

Ensure Ollama is running with `ollama serve` or check if it started automatically as a service.

## Security Considerations

- The current implementation provides **read-only** access to the file system
- All operations include permission checks and error handling
- The server runs on `localhost` only, not accessible from network
- Consider implementing authentication before exposing to network

## Future Enhancements

- Add write operations (create, modify, delete files)
- Process management tools (list, start, stop processes)
- System monitoring (CPU, memory, disk usage)
- File search and pattern matching
- User authentication and authorization
- Logging and audit trails

## License

This project is for educational purposes as part of the ASO (Operating Systems Administration) course.

## Authors

Created as part of Year 4 ASO Project, Phase 1
