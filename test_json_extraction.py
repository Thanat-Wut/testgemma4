#!/usr/bin/env python3
"""Test invoice extraction with JSON format"""
import json
import ollama

print("Testing invoice extraction with JSON format...")
print("=" * 70)

extraction_prompt = """Extract invoice details from the following text and return ONLY valid JSON (no markdown, no extra text):

Invoice Text:
---
Invoice Number: INV-2024-12345
Date: 2024-04-15
Customer: ABC Corporation
Items:
  - Laptop qty 2 @ 25,000 = 50,000
  - Monitor qty 1 @ 5,000 = 5,000
Total: 55,000
PO Number: PO-2024-001
---

JSON Schema: {"invoice_number": "string", "customer": "string", "total_amount": number, "po_number": "string"}

ONLY JSON, NO OTHER TEXT:"""

try:
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt=extraction_prompt,
        stream=False
    )
    
    response_text = response.response.strip()
    print(f"\n🤖 Model Response:\n{response_text}\n")
    
    # Try to parse JSON
    try:
        # Find JSON in response (in case there's extra text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            print(f"✅ Parsed JSON successfully!")
            print(json.dumps(parsed, indent=2))
        else:
            print(f"⚠️ No JSON found in response")
            
    except Exception as parse_err:
        print(f"❌ JSON parse failed: {parse_err}")
        print(f"Response was: {response_text[:200]}")
            
except Exception as e:
    print(f"\n❌ API Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
