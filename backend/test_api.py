import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("Testing API...")
    try:
        # 1. Start Browser
        print("Starting browser...")
        res = requests.post(f"{BASE_URL}/browser/start")
        print(f"Response: {res.json()}")

        # 2. Navigate
        print("\nNavigating...")
        res = requests.post(f"{BASE_URL}/record/navigate", json={"url": "https://www.google.com"})
        print(f"Response: {res.json()}")

        # 3. Get Steps
        print("\nGetting steps...")
        res = requests.get(f"{BASE_URL}/record/steps")
        steps = res.json().get("steps", [])
        print(f"Total steps: {len(steps)}")

        # 4. Generate Python Script
        print("\nGenerating script...")
        res = requests.get(f"{BASE_URL}/generate/python")
        script = res.json().get("script", "")
        print(f"Python script generated ({len(script)} chars)")

        # 5. Stop Browser
        print("\nStopping browser...")
        res = requests.post(f"{BASE_URL}/browser/stop")
        print(f"Response: {res.json()}")

    except Exception as e:
        print(f"API Test Failed: {e}")

if __name__ == "__main__":
    test_api()
