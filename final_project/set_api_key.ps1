# PowerShell script to set Gemini API key
# Run this script before starting the server

$apiKey = Read-Host "Enter your Gemini API key"

if ($apiKey) {
    $env:GEMINI_API_KEY = $apiKey
    Write-Host "API key set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now you can run the server with:"
    Write-Host "  python scripts\view_articles_hybrid_llm.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or run the server directly:"
    Write-Host "  python scripts\view_articles_hybrid_llm.py" -ForegroundColor Yellow
} else {
    Write-Host "No API key provided!" -ForegroundColor Red
}




