@echo off
setlocal enabledelayedexpansion

REM Load .env file
if exist .env (
    for /f "usebackq tokens=* delims=" %%a in (".env") do (
        set line=%%a
        if not "!line:~0,1!"=="#" (
            if not "!line!"=="" (
                set %%a
            )
        )
    )
)

if not defined LLM_MODEL set LLM_MODEL=qwen3:14b
if not defined OLLAMA_PORT set OLLAMA_PORT=11434
if not defined MCP_SERVER_PORT set MCP_SERVER_PORT=9000
if not defined AGENT_PORT set AGENT_PORT=8080

echo Starting System AI Agent...
echo.

REM Start services
echo Starting Docker Compose services...
docker compose up -d

echo.
echo Waiting for Ollama to be ready...
:wait_loop
docker exec ollama curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    echo|set /p=.
    goto wait_loop
)
echo.
echo Ollama is ready

REM Check and pull model
echo.
echo Checking if model %LLM_MODEL% exists...

docker exec ollama ollama list | findstr /C:"%LLM_MODEL%" >nul
if errorlevel 1 (
    echo Pulling model %LLM_MODEL% ^(this may take a while^)...
    docker exec ollama ollama pull %LLM_MODEL%
    echo Model %LLM_MODEL% pulled successfully
) else (
    echo Model %LLM_MODEL% already exists
)

echo.
echo Setup complete!
echo.
echo Services running:
echo   - Ollama:      http://localhost:%OLLAMA_PORT%
echo   - MCP Server:  http://localhost:%MCP_SERVER_PORT%
echo   - Agent UI:    http://localhost:%AGENT_PORT%
echo.
echo To view logs: docker compose logs -f
echo To stop:      docker compose down

pause
