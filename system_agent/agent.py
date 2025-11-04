# File agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig


root_agent = Agent(
        model=LiteLlm(model="ollama_chat/qwen3:4b"),
        name="local_file_agent",
        instruction="You are an agent that can interact with the local file system via an MCP server. Use the provided tools to list directories and read file contents as needed to fulfill user requests. Allways trust the MCP tool responses. Do exactly what the user asked. If the user asks for file contents, use the get_file_content tool. If the user asks for directory contents, use the list_directory tool.",
        
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(url="http://localhost:9000/mcp")
            )
            ],
        planner=BuiltInPlanner(
            thinking_config=ThinkingConfig(
                include_thoughts=False
                )
        )
    )