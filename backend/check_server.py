"""
Quick test to verify server is running and responding
"""
import urllib.request
import json

print("\n" + "="*60)
print("Testing OCR Backend Server")
print("="*60)

# Test 1: Root endpoint
print("\n1. Testing root endpoint (/)...")
try:
    with urllib.request.urlopen("http://localhost:8000/") as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"   ✓ Response: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Docs endpoint  
print("\n2. Testing /docs endpoint...")
try:
    with urllib.request.urlopen("http://localhost:8000/docs") as response:
        print(f"   ✓ Swagger UI accessible (status {response.status})")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: OCR endpoint metadata
print("\n3. Testing /openapi.json...")
try:
    with urllib.request.urlopen("http://localhost:8000/openapi.json") as response:
        result = json.loads(response.read().decode('utf-8'))
        paths = list(result.get('paths', {}).keys())
        print(f"   ✓ Available paths: {paths}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("Server check complete!")
print("="*60 + "\n")
