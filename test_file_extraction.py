#!/usr/bin/env python3
"""Test PDF and text file extraction"""
from io import BytesIO
from pypdf import PdfWriter, PdfReader
import sys
sys.path.insert(0, '.')

# Create a test PDF
def create_test_pdf():
    """Create a simple test PDF with invoice content"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # Write invoice content
        y = 750
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "INVOICE")
        
        y -= 40
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Date: 2024-04-15")
        y -= 20
        c.drawString(50, y, "Invoice Number: INV-PDF-001")
        y -= 20
        c.drawString(50, y, "Company: PDF Test Corp")
        y -= 20
        c.drawString(50, y, "Tax ID: 9876543210987")
        y -= 40
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Line Items:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "1. Desktop Computer - Qty: 3 @ $5,000 = $15,000")
        y -= 20
        c.drawString(50, y, "2. Keyboard - Qty: 3 @ $500 = $1,500")
        y -= 40
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"Total: $16,500")
        y -= 20
        c.drawString(50, y, "PO Reference: PO-PDF-001")
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.read()
    except ImportError:
        print("⚠️ reportlab not installed, creating simple PDF instead...")
        # Simple PDF: just binary data with invoice text
        pdf_bytes = b"%PDF-1.4\n"
        pdf_bytes += b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        pdf_bytes += b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        pdf_bytes += b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        pdf_bytes += b"4 0 obj\n<< >>\nstream\nBT /F1 12 Tf 50 700 Td (INVOICE) Tj ET\nendstream\nendobj\n"
        pdf_bytes += b"xref\n0 5\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
        return pdf_bytes

print("Testing file extraction...")
print("=" * 70)

# Import the function
from app import extract_file_content

# Test 1: Text file
print("\n📄 Test 1: Text File")
print("-" * 70)

class FakeUploadedFile:
    def __init__(self, content, filename):
        self.content = content
        self.name = filename
        self.position = 0
    
    def read(self):
        return self.content

text_content = """
INVOICE
Date: 2024-04-15
Company: Text Test Corp
Tax ID: 1111111111111

Items:
- Item 1: $1,000
- Item 2: $2,000

Total: $3,000
PO: PO-TEXT-001
"""

text_file = FakeUploadedFile(text_content.encode('utf-8'), "invoice.txt")
result = extract_file_content(text_file)

if result and "Text Test Corp" in result:
    print(f"✅ Text extraction PASSED")
    print(f"   Extracted {len(result)} characters")
    if "PO-TEXT-001" in result:
        print(f"   ✓ PO number found: PO-TEXT-001")
else:
    print(f"❌ Text extraction FAILED")
    print(f"   Result: {result[:100] if result else 'None'}")

# Test 2: PDF file
print("\n📄 Test 2: PDF File")
print("-" * 70)

try:
    pdf_bytes = create_test_pdf()
    pdf_file = FakeUploadedFile(pdf_bytes, "invoice.pdf")
    result = extract_file_content(pdf_file)
    
    if result and len(result) > 20:
        print(f"✅ PDF extraction PASSED")
        print(f"   Extracted {len(result)} characters")
        print(f"   Content preview: {result[:100]}...")
        if "PO" in result.upper():
            print(f"   ✓ PO reference found in PDF")
    else:
        print(f"❌ PDF extraction FAILED or empty")
        print(f"   Result: {result[:100] if result else 'None'}")
except Exception as e:
    print(f"⚠️ PDF test error: {e}")

print("\n" + "=" * 70)
