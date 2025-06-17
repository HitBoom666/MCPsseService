@echo off
echo Starting AIKnowledgeStorage MCP Server...
echo Activating conda environment: AIKnowledgeStorage
call conda activate AIKnowledgeStorage
if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment AIKnowledgeStorage
    echo Please make sure conda is installed and the environment exists
    pause
    exit /b 1
)
echo Environment activated successfully

echo.
echo Starting SSE Server in background...
echo Server will be available at: http://localhost:8000/sse
start "SSE Server" cmd /k "conda activate AIKnowledgeStorage && python server.py"

echo.
echo Waiting for SSE server to start up...
timeout /t 5 /nobreak >nul

echo.
echo Setting MCP environment variable...
set MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjI4MjM4MywiYWdlbnRJZCI6NDAzOTUwLCJlbmRwb2ludElkIjoiYWdlbnRfNDAzOTUwIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc0OTczMDYzM30.tF_YMI9nnkiv8xVoOtqf5A8q1S1NJz3evLwXG4J5K3120pbqkk6lV37W6Qj-qxnXeS5Cji4aA7S5VGIerilnMw

echo.
echo Starting MCP Pipe connection...
echo Connecting to SSE endpoint: http://localhost:8000/sse
echo MCP Endpoint: %MCP_ENDPOINT%
echo.

python mcp_pipe.py http://localhost:8000/sse

echo.
echo MCP Pipe connection ended.
pause 