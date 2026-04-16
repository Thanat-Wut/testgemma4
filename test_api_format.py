#!/usr/bin/env python3
"""Test to see what Ollama API actually returns"""
import ollama

print("Testing API response format for gemma4:31b-cloud...")
print("=" * 70)

try:
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt="What is 2+2? Answer with just the number.",
        stream=False
    )
    
    print(f"\n📊 Response Type: {type(response).__name__}")
    print(f"📋 response field: {response.response}")
    print(f"📋 model: {response.model}")
    print(f"📋 done: {response.done}")
    
except Exception as e:
    print(f"\n❌ API Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
