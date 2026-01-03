"""
Debug script to test Gemini API directly
"""

import os
import sys
import google.generativeai as genai
import traceback

# Get API key from environment variable (REQUIRED)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set!")
    print("Set it with: export GEMINI_API_KEY=your_key (Linux/Mac) or $env:GEMINI_API_KEY='your_key' (Windows)")
    sys.exit(1)

try:
    print("Configuring API...")
    genai.configure(api_key=GEMINI_API_KEY)
    print("OK: API configured")
    
    print("\nCreating model...")
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("OK: Model created")
    
    print("\nTesting generate_content...")
    response = model.generate_content("Say hello in one sentence")
    print("OK: Response received")
    
    print("\nResponse type:", type(response))
    print("Response attributes:", dir(response))
    
    print("\nTrying to get text...")
    if hasattr(response, 'text'):
        print("OK: response.text exists")
        print("Response text:", response.text[:100] if response.text else "None")
    else:
        print("ERROR: response.text does not exist")
    
    if hasattr(response, 'candidates'):
        print("\nCandidates:", len(response.candidates) if response.candidates else 0)
        if response.candidates:
            print("First candidate:", type(response.candidates[0]))
            print("First candidate attributes:", dir(response.candidates[0]))
    
    print("\n=== SUCCESS ===")
    print("Full response text:", response.text)
    
except Exception as e:
    print("\n=== ERROR ===")
    print("Error:", str(e))
    print("\nFull traceback:")
    traceback.print_exc()


