@echo off
echo ========================================
echo Starting Hybrid LLM Server
echo ========================================
echo.

cd /d "%~dp0"

echo IMPORTANT: You need to set your Gemini API key first!
echo.
echo Option 1: Set environment variable before running:
echo   set GEMINI_API_KEY=your_key_here
echo.
echo Option 2: Use start_with_api_key.bat (will prompt for key)
echo.
echo Option 3: Run in PowerShell:
echo   $env:GEMINI_API_KEY="your_key_here"
echo   python scripts\view_articles_hybrid_llm.py
echo.

if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY not set!
    echo Gemini features will not work.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        echo Exiting...
        pause
        exit /b 1
    )
)

echo Starting server on port 8002...
echo.
python scripts\view_articles_hybrid_llm.py

pause


