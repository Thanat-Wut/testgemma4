#!/usr/bin/env python3
"""Simple test of extraction function with diagnostics."""

from invoice_verification_agent import extract_invoice_data, MODEL_TO_USE
import json

print(f"Testing extraction with model: {MODEL_TO_USE}\n")
print("=" * 70)

# Test with realistic invoice content
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

print("📄 Testing with invoice:")
print(sample_invoice)
print("=" * 70)

result = extract_invoice_data(sample_invoice)

print(f"\n📊 Extracted Data:")
print(json.dumps(result, indent=2))

# Verify expected fields
expected_fields = ["company_name", "tax_id", "items", "grand_total", "po_number"]
missing = [f for f in expected_fields if f not in result]
if missing:
    print(f"\n⚠️ Missing fields: {missing}")
else:
    print(f"\n✅ All required fields present")

