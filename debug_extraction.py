#!/usr/bin/env python3
"""Debug what the model is returning for invoice extraction"""
import json
import ollama
import re

print("Debugging invoice extraction response...")
print("=" * 70)

sample_text = """
INVOICE
Date: 2024-04-15
Invoice #: INV-2024-001
 
Bill To:
Company: ABC Corporation
Tax ID: 1234567890123

Items:
1. Laptop - Qty: 2 - Unit Price: $25,000 - Total: $50,000
2. Mouse - Qty: 5 - Unit Price: $2,000 - Total: $10,000

Total Amount: $60,000
PO Number: PO-2024-001
"""

prompt = f"""Extract invoice information from the following text.
Return ONLY a valid JSON object with no markdown, no code blocks, no extra text.

The JSON must have exactly these fields:
- company_name (string)
- tax_id (string)
- items (array of objects with: name, qty, unit_price, total_price)
- grand_total (number)
- po_number (string)

Invoice text:
{sample_text}

IMPORTANT: Return ONLY the JSON object, starting with {{ and ending with }}, no other text:"""

try:
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt=prompt,
        stream=False
    )
    
    response_text = response.response.strip()
    print(f"\n🤖 Raw Response:\n{response_text}\n")
    
    # Try to extract JSON
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        print(f"📋 Extracted JSON:\n{json_str}\n")
        
        try:
            parsed = json.loads(json_str)
            print(f"✅ Parsed successfully:")
            print(json.dumps(parsed, indent=2))
        except Exception as e:
            print(f"❌ JSON parse error: {e}")
    else:
        print("❌ No JSON found in response")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
