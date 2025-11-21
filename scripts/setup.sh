#!/bin/bash
set -e

# Load .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

MODEL_NAME="${LLM_MODEL:-qwen3:14b}"

echo "Starting System AI Agent..."
echo

# Start services
echo "Starting Docker Compose services..."
docker compose up --build -d


# Check and pull model
echo
echo "Checking if model $MODEL_NAME exists..."

if docker exec ollama ollama list | grep -q "$MODEL_NAME"; then
    echo "Model $MODEL_NAME already exists"
else
    echo "Pulling model $MODEL_NAME (this may take a while)..."
    echo "If this times out, try manually: docker exec ollama ollama pull $MODEL_NAME"
    docker exec ollama ollama pull "$MODEL_NAME" || {
        echo "ERROR: Failed to pull model. Check your network connection or try:"
        echo "  1. docker exec -it ollama ollama pull $MODEL_NAME"
        echo "  2. Configure proxy if behind firewall"
        echo "  3. Use different model mirror if available"
        exit 1
    }
    echo "Model $MODEL_NAME pulled successfully"
fi

echo
echo "Setup complete!"
echo
echo "Services running:"
echo "  - Ollama:      http://localhost:${OLLAMA_PORT:-11434}"
echo "  - MCP Server:  http://localhost:${MCP_SERVER_PORT:-9000}"
echo "  - Agent UI:    http://localhost:${AGENT_PORT:-8080}"
echo
echo "To view logs: docker compose logs -f"
echo "To stop:      docker compose down"
