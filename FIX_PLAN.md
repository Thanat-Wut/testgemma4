# 🔧 Bug Fix Plan - All 13 Bugs

## 📋 Executive Plan

**Total Bugs:** 13  
**Fix Phases:** 4  
**Estimated Time:** 30-45 minutes  
**Dependencies:** Python 3.11+, streamlit, pandas, sqlite3

---

## 🎯 Phase 1: GET APP RUNNING (CRITICAL - DO FIRST)

These bugs prevent the app from starting at all.

### Priority 1.1 - Bug #1: Auto-Initialize Database
**Status:** Not Started  
**File:** [app.py](app.py#L65)  
**Fix Type:** Add initialization check  

**Current:**
```python
@st.cache_resource
def get_db_connection():
    """Get or create database connection."""
    return sqlite3.connect("invoice_verification.db", check_same_thread=False)
```

**Target:** Check if DB exists, auto-create if missing
```python
@st.cache_resource
def get_db_connection():
    """Get or create database connection."""
    if not os.path.exists("invoice_verification.db"):
        # Auto-initialize database
        from setup_mock_database import create_mock_database
        create_mock_database()
    return sqlite3.connect("invoice_verification.db", check_same_thread=False)
```

**Dependencies:** Needs import `os`

---

### Priority 1.2 - Bug #3: Handle Ollama Connection Gracefully
**Status:** Not Started  
**File:** [invoice_verification_agent.py](invoice_verification_agent.py#L33)  
**Fix Type:** Add connection timeout and better error handling  

**Current:**
```python
try:
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt=prompt,
        stream=False
    )
```

**Target:** Check if Ollama is available with timeout
```python
try:
    # Check if Ollama is available (timeout after 2 seconds)
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt=prompt,
        stream=False,
        timeout=2  # Add timeout
    )
```

**Alternative:** Add connection check before calling
```python
import socket

def is_ollama_available(host="127.0.0.1", port=11434, timeout=1):
    """Check if Ollama server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()
```

---

### Priority 1.3 - Bug #2: Verify Dependencies (Diagnostic)
**Status:** Not Started  
**File:** N/A (Terminal command)  
**Fix Type:** Pre-flight checks  

**Commands:**
```bash
# 1. Check Python version
python --version
# Expected: 3.11 or higher

# 2. Install dependencies
pip install streamlit pandas sqlite3

# 3. Verify installations
python -c "import streamlit, pandas, sqlite3; print('All dependencies OK')"

# 4. Check if Ollama is running (optional)
curl http://127.0.0.1:11434/api/tags
# If connection refused, Ollama not running
```

---

## 🔄 Phase 2: FIX DATA PROCESSING (HIGH PRIORITY)

These bugs cause incorrect data flow through the system.

### Priority 2.1 - Bug #5: Actually Read Uploaded File Content
**Status:** Not Started  
**File:** [app.py](app.py#L200)  
**Fix Type:** Read file instead of using mock  

**Current:**
```python
with st.spinner("🤖 Extracting invoice data using LLM..."):
    invoice_data = extract_invoice_data(f"Mock content from {invoice_filename}")
```

**Target:**
```python
with st.spinner("🤖 Extracting invoice data using LLM..."):
    # Read actual file content
    file_content = uploaded_file.read().decode('utf-8', errors='ignore')
    invoice_data = extract_invoice_data(file_content)
```

**Note:** Handle binary files (PDF) - might need OCR library

---

### Priority 2.2 - Bug #9: Add PO Number Validation
**Status:** Not Started  
**File:** [invoice_verification_agent.py](invoice_verification_agent.py#L97)  
**Fix Type:** Add validation before query  

**Current:**
```python
po_number = invoice_json.get("po_number")

cursor.execute(
    "SELECT po_number, vendor_name, expected_total_amount, status FROM purchase_orders WHERE po_number = ?",
    (po_number,)
)
```

**Target:**
```python
po_number = invoice_json.get("po_number", "").strip()

# Rule 0: Validate PO number exists
if not po_number:
    status = "ERROR"
    message = "PO number is missing from invoice"
    print(f"❌ {status}: {message}")
    return (status, message)

cursor.execute(
    "SELECT po_number, vendor_name, expected_total_amount, status FROM purchase_orders WHERE po_number = ?",
    (po_number,)
)
```

---

### Priority 2.3 - Bug #10: Validate JSON Schema from LLM
**Status:** Not Started  
**File:** [invoice_verification_agent.py](invoice_verification_agent.py#L42)  
**Fix Type:** Add schema validation  

**Current:**
```python
response_text = response['response'].strip()
extracted_data = json.loads(response_text)
```

**Target:**
```python
response_text = response['response'].strip()
extracted_data = json.loads(response_text)

# Validate required fields
required_fields = ["company_name", "tax_id", "items", "grand_total", "po_number"]
missing_fields = [f for f in required_fields if f not in extracted_data]

if missing_fields:
    print(f"⚠️ Missing fields in LLM response: {missing_fields}")
    print("Falling back to mock data...")
    return fallback_data  # Use fallback
```

---

### Priority 2.4 - Bug #7: Fix Test Case Data
**Status:** Not Started  
**File:** [invoice_verification_agent.py](invoice_verification_agent.py#L245)  
**Fix Type:** Use correct PO amounts  

**Current:**
```python
invalid_invoice = {
    ...
    "grand_total": 60000,  # WRONG - PO-2024-001 expects $15,500
    "po_number": "PO-2024-001"
}
```

**Target:**
```python
# Updated mock PO values from setup_mock_database.py:
# PO-2024-001: $15,500.00
# PO-2024-002: $8,750.50
# PO-2024-003: $22,300.75

invalid_invoice = {
    "company_name": "ABC Corp",
    "tax_id": "1234567890123",
    "items": [
        {
            "name": "Laptop",
            "qty": 2,
            "unit_price": 25000,
            "total_price": 50000
        }
    ],
    "grand_total": 20000,  # CORRECTED - Different from $15,500 to trigger mismatch
    "po_number": "PO-2024-001"
}
```

---

## 🗄️ Phase 3: FIX DATABASE ISSUES

### Priority 3.1 - Bug #4: Fix Foreign Key Constraint Issue
**Status:** Not Started  
**File:** [setup_mock_database.py](setup_mock_database.py#L43-44) & [invoice_verification_agent.py](invoice_verification_agent.py#L155)  
**Fix Type:** Handle constraint violation  

**Problem:** When PO doesn't exist, logging ERROR crashes because of foreign key constraint

**Solution A: Remove Foreign Key Constraint** (Easier)
```python
# In setup_mock_database.py, remove the FOREIGN KEY line:
cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_filename TEXT NOT NULL,
        po_number TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        approved_by TEXT
        -- Removed: FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number)
    )
""")
```

**Solution B: Handle Gracefully in Code** (Better)
```python
def log_verification_result(...):
    cursor = db_connection.cursor()
    
    # Check if PO exists before logging
    cursor.execute(
        "SELECT po_number FROM purchase_orders WHERE po_number = ?",
        (po_number,)
    )
    
    if cursor.fetchone() is None and verification_status == "ERROR":
        print(f"⚠️ Warning: PO {po_number} not found, skipping audit log for ERROR status")
        return None  # Don't log ERROR for non-existent POs
    
    # Normal logging...
    cursor.execute("""...""")
```

---

## 📝 Phase 4: CODE QUALITY IMPROVEMENTS

### Priority 4.1 - Bug #6: Remove Unused Import
**Status:** Not Started  
**File:** [app.py](app.py#L11)  
**Fix Type:** Delete line  

**Current:**
```python
from io import StringIO  # ← LINE 11 - REMOVE THIS
```

**Target:** Delete the line entirely

---

### Priority 4.2 - Bug #10: Remove Dead Session State Code
**Status:** Not Started  
**File:** [app.py](app.py#L75, L244, L309)  
**Fix Type:** Delete unused code blocks  

**Current:**
```python
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "approval_status" not in st.session_state:
        st.session_state.approval_status = {}  # ← UNUSED
```

**Then Later:**
```python
st.session_state.approval_status[invoice_filename] = "APPROVED"  # ← NEVER CHECKED
st.session_state.approval_status[invoice_filename] = "REJECTED"  # ← NEVER CHECKED
```

**Target:** Either use it for persistence or remove all three blocks

---

### Priority 4.3 - Bug #7: Parameterize Mock Data
**Status:** Not Started  
**File:** [invoice_verification_agent.py](invoice_verification_agent.py#L59-73)  
**Fix Type:** Make mock data flexible  

**Current:**
```python
fallback_data = {
    "company_name": "ABC Corp",
    "tax_id": "1234567890123",
    "items": [...],
    "grand_total": 50000,  # ← HARDCODED
    "po_number": "PO-2024-001"  # ← HARDCODED
}
```

**Target: Extract as parameter or from config**
```python
MOCK_INVOICE_DATA = {
    "company_name": "ABC Corp",
    "tax_id": "1234567890123",
    "items": [
        {"name": "Laptop", "qty": 2, "unit_price": 25000, "total_price": 50000}
    ],
    "grand_total": 50000,
    "po_number": "PO-2024-001"
}

def extract_invoice_data(text: str, use_default_mock: bool = True) -> Dict[str, Any]:
    # ...
    return MOCK_INVOICE_DATA.copy()  # Use copy to avoid mutation
```

---

### Priority 4.4 - Bug #12: Optimize Timestamp Conversion
**Status:** Not Started  
**File:** [app.py](app.py#L103)  
**Fix Type:** Simplify conversion chain  

**Current:**
```python
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
```

**Target:**
```python
# Option 1: Direct string formatting (if already datetime)
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Option 2: Format in SQL query (most efficient)
# SELECT datetime(timestamp, 'localtime') FROM audit_log
```

---

### Priority 4.5 - Bug #13: Add Database Connection Cleanup
**Status:** Not Started  
**File:** [app.py](app.py#L1)  
**Fix Type:** Add connection lifecycle management  

**Target:** Add cleanup callback
```python
import streamlit as st
import atexit

@st.cache_resource
def get_db_connection():
    """Get or create database connection."""
    conn = sqlite3.connect("invoice_verification.db", check_same_thread=False)
    
    # Register cleanup on exit
    def cleanup():
        try:
            conn.close()
            print("🔌 Database connection closed")
        except:
            pass
    
    atexit.register(cleanup)
    return conn
```

---

## 📊 Fix Priority Matrix

| Phase | Priority | Bugs | Dependencies | Time |
|-------|----------|------|--------------|------|
| 1 | CRITICAL | #1, #3, #2 | Must do first | 10 min |
| 2 | HIGH | #5, #9, #10, #7 | Need Phase 1 | 15 min |
| 3 | HIGH | #4 | Need Phase 2 | 5 min |
| 4 | MEDIUM | #6, #11, #7*, #12, #13 | Optional | 15 min |

---

## ✅ Testing Checklist After Fixes

- [ ] `streamlit run app.py` starts without errors
- [ ] Database auto-creates if missing
- [ ] Upload a PDF/image file → processes actual content (not mock)
- [ ] PO number validation rejects empty PO numbers
- [ ] ERROR status doesn't crash database
- [ ] JSON schema validation catches malformed responses
- [ ] Test case 2 correctly triggers FAILED status
- [ ] No unused imports remain
- [ ] Code runs without session state warnings
- [ ] Timestamps display correctly in audit log
- [ ] No orphaned database connections on restart

---

## 🚀 Recommended Fix Order

1. ✅ **Bug #1** - Auto-init database (unblocks everything)
2. ✅ **Bug #3** - Handle Ollama gracefully (prevents crash)
3. ✅ **Bug #2** - Verify dependencies (diagnostic)
4. ✅ **Bug #5** - Read actual file content (core feature)
5. ✅ **Bug #9** - Validate PO number (data integrity)
6. ✅ **Bug #10** - Validate JSON schema (error prevention)
7. ✅ **Bug #7** - Fix test data (correctness)
8. ✅ **Bug #4** - Fix foreign key (database stability)
9. ✅ **Bug #6** - Remove unused import (clean code)
10. ✅ **Bug #11** - Remove dead code (clean code)
11. ✅ **Bug #12** - Optimize timestamps (performance)
12. ✅ **Bug #13** - Add cleanup (lifecycle)

---

## 💾 Files to Modify

- [app.py](app.py) - Bugs: #1, #2, #5, #6, #11, #12, #13
- [invoice_verification_agent.py](invoice_verification_agent.py) - Bugs: #3, #4, #7, #9, #10
- [setup_mock_database.py](setup_mock_database.py) - Bug: #4 (optional)

---

Ready to start fixing? Let me know which phase to begin with!
