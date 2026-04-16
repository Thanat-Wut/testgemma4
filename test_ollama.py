#!/usr/bin/env python3
"""Test Ollama LLM connection and diagnose issues."""

import ollama
import json

print("🧪 Testing Ollama LLM Connection...")
print("=" * 70)

try:
    print("\n1️⃣ Attempting to call gemma4:31b-cloud...")
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt="What is 2+2?",
        stream=False
    )
    print("✅ SUCCESS! LLM responded")
    print(f"   Response Length: {len(response['response'])} characters")
    print(f"   Response: {response['response'][:150]}...")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    
    # Try to diagnose
    print("\n2️⃣ Diagnostic Information:")
    
    # Check API availability
    import requests
    try:
        tags_resp = requests.get('http://127.0.0.1:11434/api/tags', timeout=2)
        print(f"   ✓ Ollama API Status: {tags_resp.status_code}")
        models = tags_resp.json()['models']
        print(f"   ✓ Available Models: {len(models)}")
        for m in models:
            print(f"     - {m['name']}")
    except Exception as api_err:
        print(f"   ✗ Cannot reach Ollama API: {api_err}")
    
    # Check if it's a cloud model issue
    print(f"\n3️⃣ Analyzing Error:")
    if "401" in str(e):
        print("   ℹ️ This is an authorization error (401)")
        print("   Possible causes:")
        print("   - Cloud model might require authentication")
        print("   - API key might be missing or invalid")
        print("   - Model endpoint might be restricted")
    elif "Connection" in str(e):
        print("   ℹ️ This is a connection error")
        print("   Please ensure Ollama is running")
    
    print("\n4️⃣ Recommendations:")
    print("   • Pull a local model instead: ollama pull gemma2")
    print("   • Or check cloud model authentication")
    print("   • Current fallback will use mock data (OK)")

print("\n" + "=" * 70)
