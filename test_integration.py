#!/usr/bin/env python3
"""
Integration test for AI Search Engine with Python Execution API
Tests all endpoints to ensure they work correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_status():
    """Test status endpoint"""
    print("Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"  Uptime: {data.get('uptime', 'N/A')}")
    print(f"  Searches: {data.get('search_requests', 'N/A')}")
    return response.status_code == 200

def test_search():
    """Test search endpoint"""
    print("Testing search endpoint...")
    query = "python programming"
    response = requests.get(f"{BASE_URL}/search?q={query}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"Search: Found {data.get('count', 0)} results")
        if data.get('results'):
            print(f"  First result: {data['results'][0].get('title', 'N/A')}")
        return True
    else:
        print(f"Search failed: {data}")
        return False

def test_classify():
    """Test classification endpoint"""
    print("Testing classification endpoint...")
    text = "I love this amazing product!"
    response = requests.get(f"{BASE_URL}/classify?text={text}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"Classification: {data.get('emotion', 'N/A')}")
        print(f"  Confidence: {data.get('confidence', 'N/A')}")
        return True
    else:
        print(f"Classification failed: {data}")
        return False

def test_python_execution():
    """Test Python execution endpoint"""
    print("Testing Python execution endpoint...")
    
    # Test basic execution
    code = """
print("Hello from Python!")
a = 5
b = 10
print(f"Sum: {a + b}")
print(f"Product: {a * b}")
"""
    
    response = requests.post(f"{BASE_URL}/execute", 
                           json={"code": code},
                           headers={"Content-Type": "application/json"})
    data = response.json()
    
    if response.status_code == 200:
        print(f"Python execution: Success")
        print(f"  Output: {data.get('output', 'N/A').strip()}")
        print(f"  Execution time: {data.get('execution_time', 'N/A')}s")
        return True
    else:
        print(f"Python execution failed: {data}")
        return False

def test_security():
    """Test security features"""
    print("Testing security features...")
    
    # Test dangerous code blocking
    dangerous_code = """
import os
print("This should be blocked")
"""
    
    response = requests.post(f"{BASE_URL}/execute", 
                           json={"code": dangerous_code},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 403:
        print("Security: Dangerous code properly blocked")
        return True
    else:
        print(f"Security test failed: {response.json()}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Search Engine Integration Tests")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ Server not responding after 30 seconds")
        return
    
    tests = [
        ("Health Check", test_health),
        ("Status", test_status),
        ("Search", test_search),
        ("Classification", test_classify),
        ("Python Execution", test_python_execution),
        ("Security", test_security)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()