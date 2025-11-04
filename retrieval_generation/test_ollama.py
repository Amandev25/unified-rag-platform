"""
Quick test to check if Ollama endpoint is working
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_ollama():
    # Get Ollama URL from environment or use default
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "gemma:2b")
    
    # Add ngrok auth token if needed (optional)
    ngrok_auth = os.getenv("NGROK_AUTH_TOKEN", "34SzIeER6zuHC9FCXZhawouTkTH_54ormQNBppgnPNYToc3q6")
    headers = {}
    if ngrok_auth:
        headers["ngrok-skip-browser-warning"] = "true"
        # headers["Authorization"] = f"Bearer {ngrok_auth}"  # Uncomment if using auth token
    
    print("=" * 60)
    print("Testing Ollama Endpoint")
    print("=" * 60)
    print(f"\nURL: {ollama_url}")
    print(f"Model: {model}")
    print(f"Auth headers: {'Yes' if headers else 'No'}")
    
    # Test 1: Check if Ollama is running
    print("\n[Test 1] Checking if Ollama server is reachable...")
    try:
        response = requests.get(f"{ollama_url}/api/tags", headers=headers, timeout=5)
        print(f"✅ Server is reachable! Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"   Available models: {len(models)}")
            for m in models[:5]:  # Show first 5 models
                print(f"     - {m.get('name', 'unknown')}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server")
        print(f"   Make sure Ollama is running at {ollama_url}")
        print("\n   To start Ollama:")
        print("     1. Open a terminal")
        print("     2. Run: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Try a simple generation
    print(f"\n[Test 2] Testing generation with model '{model}'...")
    try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Say 'Hello!' in one word."}],
            "stream": False
        }
        
        print("   Sending test request...")
        response = requests.post(
            f"{ollama_url}/api/chat",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Try to extract response
            answer = None
            if 'message' in data and 'content' in data['message']:
                answer = data['message']['content']
            elif 'choices' in data and len(data['choices']) > 0:
                if 'message' in data['choices'][0]:
                    answer = data['choices'][0]['message'].get('content')
            
            if answer:
                print(f"✅ Generation successful!")
                print(f"   Response: {answer.strip()}")
                return True
            else:
                print(f"⚠️  Got response but couldn't parse it")
                print(f"   Raw response: {json.dumps(data, indent=2)[:200]}...")
                return True
        else:
            print(f"❌ Generation failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code == 403:
                print("\n   🔒 403 Forbidden - Possible causes:")
                print("   1. ngrok tunnel requires authentication")
                print("   2. ngrok tunnel has IP restrictions")
                print("   3. ngrok free plan limitations")
                print("\n   💡 Solutions:")
                print("   A) Use local Ollama instead:")
                print("      - Start Ollama locally: ollama serve")
                print("      - Set URL: http://localhost:11434")
                print("   B) Check ngrok dashboard for auth requirements")
                print("   C) Try using ngrok's authtoken:")
                print("      - ngrok config add-authtoken YOUR_TOKEN")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Generation timeout (model might not be loaded)")
        print(f"\n   To download the model:")
        print(f"     ollama pull {model}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_ollama()
    print("\n" + "=" * 60)
    if success:
        print("✅ Ollama endpoint is working correctly!")
    else:
        print("❌ Ollama endpoint has issues - see errors above")
    print("=" * 60)
    print()

