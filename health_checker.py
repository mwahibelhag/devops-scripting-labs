#!/usr/bin/env python3
import time
import urllib.request
import urllib.error

# قائمة الخدمات أو الروابط التي سنفحص حالتها (يمكنك تعديلها لاحقاً)
ENDPOINTS = [
    {"name": "Local Web App", "url": "http://localhost:8080"},
    {"name": "GitHub Profile", "url": "https://github.com"},
    {"name": "Google Search", "url": "https://www.google.com"},
]

def check_service(endpoint):
    try:
        req = urllib.request.Request(
            endpoint["url"],
            headers={"User-Agent": "SRE-HealthChecker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                print(f"[UP] {endpoint['name']} is healthy (Status: 200)")
                return True
    except urllib.error.HTTPError as e:
        print(f"[DOWN] {endpoint['name']} returned HTTP Error: {e.code}")
    except urllib.error.URLError as e:
        print(f"[DOWN] {endpoint['name']} is unreachable: {e.reason}")
    except Exception as e:
        print(f"[DOWN] {endpoint['name']} failed with error: {e}")
    return False

if __name__ == "__main__":
    print("=== Starting SRE Health Check Simulation ===")
    for endpoint in ENDPOINTS:
        check_service(endpoint)
    print("=== Health Check Complete ===")