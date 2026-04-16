#!/usr/bin/env python3
"""Debug what qwen3.5:397b-cloud actually returns"""
import json
import ollama
import re

print("Debugging qwen3.5:397b-cloud response...")
print("=" * 70)

sample_invoice = """
INVOICE
Date: 2024-04-15
Invoice Number: INV-001

Bill To:
ABC Corporation
Tax ID: 1234567890123

Line Items:
1. Laptop Computer - Qty: 2 @ $25,000.00 each = $50,000.00
2. Wireless Mouse - Qty: 5 @ $2,000.00 each = $10,000.00

Subtotal: $60,000.00
Tax (0%): $0.00
TOTAL: $60,000.00

PO Reference: PO-2024-001
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
{sample_invoice}

IMPORTANT: Return ONLY the JSON object, starting with {{ and ending with }}, no other text:"""

try:
    response = ollama.generate(
        model="qwen3.5:397b-cloud",
        prompt=prompt,
        stream=False
    )
    
    response_text = response.response.strip()
    print(f"\n🤖 RAW RESPONSE:\n{response_text}\n")
    print("=" * 70)
    
    # Try to extract JSON
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        print(f"\n📋 EXTRACTED JSON STRING:\n{json_str}\n")
        
        try:
            parsed = json.loads(json_str)
            print(f"\n📊 PARSED JSON:")
            print(json.dumps(parsed, indent=2))
            
            print(f"\n✅ Fields Found:")
            for key, value in parsed.items():
                if isinstance(value, str):
                    print(f"  • {key}: {value}")
                elif isinstance(value, list):
                    print(f"  • {key}: {len(value)} items")
                else:
                    print(f"  • {key}: {value}")
                    
        except Exception as e:
            print(f"❌ JSON PARSE ERROR: {e}")
            print(f"Response text: {json_str[:300]}")
    else:
        print("❌ NO JSON FOUND in response")
        print(f"Response was: {response_text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
