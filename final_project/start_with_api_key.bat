@echo off
echo ========================================
echo Starting Hybrid LLM Server
echo ========================================
echo.

cd /d "%~dp0"

echo Please enter your Gemini API key:
set /p GEMINI_API_KEY="API Key: "

if "%GEMINI_API_KEY%"=="" (
    echo ERROR: No API key provided!
    pause
    exit /b 1
)

echo.
echo Setting API key and starting server...
echo.

set GEMINI_API_KEY=%GEMINI_API_KEY%
python scripts\view_articles_hybrid_llm.py

pause




