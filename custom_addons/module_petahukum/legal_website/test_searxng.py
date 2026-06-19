# Test SearXNG Integration

import requests
import json

def test_searxng_connection():
    """Test koneksi ke SearXNG instance"""
    
    searxng_url = "https://search.brave4u.com"
    
    try:
        # Test basic search
        params = {
            'q': 'hukum pidana indonesia',
            'format': 'json',
            'engines': 'google,bing',
            'categories': 'general',
            'language': 'id',
            'safesearch': '1',
            'pageno': 1,
        }
        
        response = requests.get(
            f"{searxng_url}/search",
            params=params,
            timeout=10,
            headers={'User-Agent': 'Legal Website Test Bot'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {len(data.get('results', []))}")
            
            # Show first few results
            for i, result in enumerate(data.get('results', [])[:3]):
                print(f"\nResult {i+1}:")
                print(f"Title: {result.get('title', 'N/A')}")
                print(f"URL: {result.get('url', 'N/A')}")
                print(f"Content: {result.get('content', 'N/A')[:100]}...")
                print(f"Engine: {result.get('engine', 'N/A')}")
            
            return True
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.RequestException as e:
        print(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_alternative_instances():
    """Test alternative SearXNG instances"""
    
    instances = [
        "https://search.brave4u.com",
        "https://searxng.online", 
        "https://searx.work",
        "https://searx.tiekoetter.com"
    ]
    
    for instance in instances:
        print(f"\nTesting {instance}...")
        
        try:
            response = requests.get(
                f"{instance}/search?q=test&format=json",
                timeout=5,
                headers={'User-Agent': 'Legal Website Test Bot'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Working - {len(data.get('results', []))} results")
            else:
                print(f"✗ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    print("=== Testing SearXNG Integration ===\n")
    
    print("1. Testing default instance...")
    success = test_searxng_connection()
    
    if not success:
        print("\n2. Testing alternative instances...")
        test_alternative_instances()
    
    print("\n=== Test Complete ===")
    
    if success:
        print("✓ SearXNG integration is working!")
        print("Modul Legal Website siap digunakan.")
    else:
        print("⚠ SearXNG connection issues detected.")
        print("Periksa koneksi internet dan instance SearXNG.")