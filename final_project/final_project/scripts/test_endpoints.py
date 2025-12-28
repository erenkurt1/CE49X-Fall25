"""
Quick test script to diagnose endpoint issues
"""
import requests
import json

BASE_URL = "http://localhost:8002"

def test_endpoint(name, method, url, data=None):
    """Test an endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response OK: {len(str(json_data))} chars")
                if 'results' in json_data:
                    print(f"Results count: {json_data.get('count', 0)}")
                if 'error' in json_data:
                    print(f"ERROR in response: {json_data['error']}")
            except:
                print("Response is not JSON")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Hybrid LLM Server Endpoints")
    print("Make sure the server is running on http://localhost:8002")
    
    # Test 1: Get articles
    test_endpoint("Get Articles", "GET", f"{BASE_URL}/api/articles")
    
    # Test 2: Search
    test_endpoint("Search", "POST", f"{BASE_URL}/api/search", {
        "query": "AI construction",
        "top_k": 5
    })
    
    # Test 3: QA
    test_endpoint("QA", "POST", f"{BASE_URL}/api/qa", {
        "question": "What are the main trends in AI and construction?"
    })
    
    # Test 4: Classify
    test_endpoint("Classify", "POST", f"{BASE_URL}/api/classify", {
        "text": "This article discusses AI applications in structural engineering and machine learning for construction safety."
    })
    
    # Test 5: Chat (should work)
    test_endpoint("Chat", "POST", f"{BASE_URL}/api/chat", {
        "message": "Hello"
    })
    
    print(f"\n{'='*60}")
    print("Testing Complete")
    print(f"{'='*60}")


