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
echo Server will be available at: http://localhost:8000/sse
echo.
python server.py
pause 