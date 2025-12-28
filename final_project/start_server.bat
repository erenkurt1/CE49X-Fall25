@echo off
echo ========================================
echo Starting Hybrid LLM Server
echo ========================================
echo.

cd /d "%~dp0"
cd ..

echo Current directory: %CD%
echo.

echo Starting server on port 8002...
echo.
python scripts\view_articles_hybrid_llm.py

pause


