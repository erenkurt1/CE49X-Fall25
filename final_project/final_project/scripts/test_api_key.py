"""
Test NewsAPI Key
Quick script to verify if the API key is working
"""

from newsapi import NewsApiClient

API_KEY = 'a9c84cf1-0af7-4560-8408-3325c00abf3a'

print(f"Testing API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print("=" * 60)

try:
    newsapi = NewsApiClient(api_key=API_KEY)
    
    # Try a simple test query
    print("\nTesting API connection...")
    response = newsapi.get_everything(
        q='construction AND AI',
        language='en',
        sort_by='relevancy',
        page_size=1
    )
    
    if response['status'] == 'ok':
        print("SUCCESS: API key is valid!")
        print(f"Found {response['totalResults']} total articles")
        if response['articles']:
            print(f"Sample article: {response['articles'][0]['title']}")
    else:
        print(f"ERROR: {response.get('message', 'Unknown error')}")
        print(f"Code: {response.get('code', 'N/A')}")
        
except Exception as e:
    print(f"EXCEPTION: {str(e)}")
    if 'apiKeyInvalid' in str(e):
        print("\nThe API key appears to be invalid.")
        print("Please check:")
        print("1. Is the key correct?")
        print("2. Have you activated your NewsAPI account?")
        print("3. Is the key from https://newsapi.org?")


