"""
Test script to list available Gemini models and test API connectivity
"""

import google.generativeai as genai

# API Key
GEMINI_API_KEY = "AIzaSyBblvdDtv3zNUf6AP5U8rGapuixzHbpt74"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[OK] API key configured successfully")
    print()
    
    # List available models
    print("Available models:")
    print("=" * 50)
    models = list(genai.list_models())
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"[OK] {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description[:100] if model.description else 'N/A'}...")
            print()
    
    # Try to use a model
    print("Testing model usage...")
    print("=" * 50)
    
    # Try different model name formats (newer models first)
    model_names_to_try = [
        'models/gemini-2.0-flash-001',  # Stable newer model
        'models/gemini-2.5-flash',      # Latest stable
        'models/gemini-2.5-pro',        # Latest pro
        'models/gemini-flash-latest',   # Latest flash
        'models/gemini-pro-latest',     # Latest pro
        'models/gemini-2.0-flash',      # Alternative
        'gemini-1.5-flash',             # Old (may not work)
        'gemini-1.5-pro', 
        'gemini-pro'
    ]
    
    working_model = None
    for model_name in model_names_to_try:
        try:
            print(f"\nTrying: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"[SUCCESS] Model works: {model_name}")
            print(f"  Response: {response.text[:100]}...")
            print(f"\n[RECOMMENDED] Use this model name in your code: '{model_name}'")
            working_model = model_name
            break
        except Exception as e:
            print(f"[FAILED] {str(e)[:100]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

