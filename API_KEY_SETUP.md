# 🔐 Ollama Cloud Model Authentication Setup Guide

## การตั้งค่า API Key สำหรับ Cloud Models

---

## ✅ คุณได้ทำถูกแล้ว!

คุณรัน `ollama signin` ซึ่งเป็นขั้นตอนแรกที่ถูกต้อง

---

## 📋 ขั้นตอนการตั้งค่า API Key

### ขั้นตอนที่ 1: ลงชื่อเข้า Ollama (✅ คุณทำแล้ว)
```bash
ollama signin
```
**ผลลัพธ์ที่คาดหวัง:**
- มันจะขอให้คุณสร้าง/ใช้ Ollama account
- จะบันทึก API token ลงในระบบ

### ขั้นตอนที่ 2: ตรวจสอบว่า Token ถูกตั้งค่าแล้ว

**For Windows PowerShell:**
```powershell
# ดูว่า environment variable ถูกตั้งค่าแล้ว
echo $env:OLLAMA_API_KEY
# ควรแสดง: YOUR_API_KEY_HERE (อย่างเช่น: abc123def456...)
```

**For Windows Command Prompt:**
```cmd
echo %OLLAMA_API_KEY%
```

**For Linux/Mac:**
```bash
echo $OLLAMA_API_KEY
```

### ขั้นตอนที่ 3: ตรวจสอบ Ollama Configuration

```bash
# ตรวจสอบว่า Ollama สามารถเข้าถึง API key
ollama list
# ควรแสดง models ที่ available
```

---

## 🔧 หากยังใช้ไม่ได้ - วิธีแก้ทีละขั้นตอน

### วิธี 1: Manual Environment Variable (Windows)

**PowerShell:**
```powershell
# ตั้งค่า environment variable
$env:OLLAMA_API_KEY = "YOUR_API_KEY_HERE"

# ยืนยันว่าตั้งแล้ว
echo $env:OLLAMA_API_KEY

# เริ่ม Ollama ใหม่
ollama serve
```

**Command Prompt:**
```cmd
setx OLLAMA_API_KEY "YOUR_API_KEY_HERE"
# จากนั้น restart terminal
```

### วิธี 2: Update Python Code to Use API Key

ในไฟล์ `invoice_verification_agent.py` เพิ่ม:

```python
import os
from ollama import Client

# ตั้งค่า API key จาก environment
api_key = os.getenv("OLLAMA_API_KEY")

if api_key:
    client = Client(
        host="http://localhost:11434",
        headers={"Authorization": f"Bearer {api_key}"}
    )
else:
    client = Client(host="http://localhost:11434")

# จากนั้นใช้ client สำหรับ API calls
response = client.generate(
    model=MODEL_TO_USE,
    prompt=prompt,
    stream=False
)
```

### วิธี 3: ตรวจสอบ Ollama Version

```bash
ollama version
# Output ควร >= 0.21.0
```

---

## 🧪 Test Cloud Model After Setup

สร้างไฟล์ `test_cloud_model.py`:

```python
#!/usr/bin/env python3
import os
import ollama

print("🔐 Testing Cloud Model with Authentication...")
print("=" * 70)

# ดู API key status
api_key = os.getenv("OLLAMA_API_KEY")
if api_key:
    print(f"✓ API Key found: {api_key[:20]}...")
else:
    print("✗ API Key NOT found")
    print("  Please run: ollama signin")
    print("  Or set: $env:OLLAMA_API_KEY = 'your_key'")

print("\nTesting gemma4:31b-cloud...")

try:
    response = ollama.generate(
        model="gemma4:31b-cloud",
        prompt="What is 2+2?",
        stream=False
    )
    print("✅ SUCCESS! Cloud model is working")
    print(f"Response: {response['response'][:100]}...")
    
except Exception as e:
    error_str = str(e)
    print(f"❌ Error: {error_str}")
    
    if "401" in error_str:
        print("\n📋 SOLUTION:")
        print("  1. Run: ollama signin")
        print("  2. Set env var: $env:OLLAMA_API_KEY = 'your_token'")
        print("  3. Restart Ollama: ollama serve")
    elif "Connection" in error_str:
        print("\n📋 SOLUTION:")
        print("  Ollama not running. Start with: ollama serve")

print("=" * 70)
```

**รัน test:**
```bash
python test_cloud_model.py
```

---

## 🎯 ที่มา API Key

### ได้ API Key จากที่ไหน?

**วิธี 1: จาก Ollama (Recommended)**
```bash
ollama signin
# จะให้คุณสร้าง account หรือ login
# Token จะถูกบันทึกโดยอัตโนมัติ
```

**วิธี 2: จาก Ollama Cloud Website**
- ไปที่ https://ollama.ai
- Login หรือสร้าง account
- ไปที่ settings → API keys
- Copy API key

**วิธี 3: ตรวจสอบที่มี token แล้วหรือไม่**
```bash
# Windows
type %USERPROFILE%\.ollama\auth.json

# Linux/Mac
cat ~/.ollama/auth.json
```

---

## 📝 ตัวอย่างเต็ม - ตั้งค่า gemma4:31b-cloud

### ขั้นตอนแบบสมบูรณ์:

```bash
# 1. ลงชื่อ
ollama signin

# 2. ตรวจสอบ token (PowerShell)
echo $env:OLLAMA_API_KEY

# 3. เริ่ม Ollama ใหม่ (เพื่อให้ token โหล)
ollama serve

# 3. ในหน้าต่าง Terminal ใหม่ ทดสอบ model
ollama list
# ควรแสดง gemma4:31b-cloud

# 4. pull model (if needed)
ollama pull gemma4:31b-cloud

# 5. ทดสอบ
python test_cloud_model.py
```

---

## ⚠️ Common Issues & Solutions

| ปัญหา | สาเหตุ | วิธีแก้ |
|------|--------|--------|
| 401 Unauthorized | Token หายหรือหมดอายุ | `ollama signin` อีกครั้ง |
| API Key not found | Environment variable ไม่ตั้ง | `$env:OLLAMA_API_KEY = "..."` |
| Connection refused | Ollama ไม่ running | `ollama serve` |
| Model not found | ยังไม่ pull | `ollama pull gemma4:31b-cloud` |
| Slow response | Model ตัวใหญ่ | ปกติ ให้เวลา 30+ วินาที |

---

## 🆚 Cloud vs Local Models

| คุณสมบัติ | Cloud (`gemma4:31b-cloud`) | Local (`gemma2`) |
|----------|---------------------------|-----------------|
| คุณภาพ | ⭐⭐⭐⭐⭐ ดีที่สุด | ⭐⭐⭐⭐ ดี |
| ความเร็ว | ⚡ ช้า (30+ วิ) | ⚡⚡⚡ เร็ว (1-5 วิ) |
| ความต้องการ | 🔑 API key | ⭕ ไม่ต้อง |
| เก็บ disk | ⭕ ไม่ต้อง | 2.6 GB |
| ออนไลน์ | 🌐 ต้อง | ⭕ ไม่ต้อง |
| เหมาะสำหรับ | Production | Testing/Development |

---

## ✅ Checklist การตั้งค่า

- [ ] รัน `ollama signin`
- [ ] ตรวจสอบ token: `echo $env:OLLAMA_API_KEY`
- [ ] Token มีค่า (ไม่ว่าง)
- [ ] เริ่ม Ollama ใหม่ หลังจากตั้ง token
- [ ] รัน `python test_cloud_model.py`
- [ ] ได้ ✅ SUCCESS message

---

## 🚀 หลังตั้งค่าเสร็จแล้ว

### ตัวเลือก 1: ใช้ Cloud Model
```python
# invoice_verification_agent.py line 21
MODEL_TO_USE = "gemma4:31b-cloud"  # ✅ ใช้ได้แล้ว

# รัน app
streamlit run app.py
```

### ตัวเลือก 2: ยังใช้ Local Model (ถ้าประสบปัญหา)
```python
# invoice_verification_agent.py line 21
MODEL_TO_USE = "gemma2"  # Local model (ไม่ต้อง auth)

# รัน app
streamlit run app.py
```

---

## 💡 ทำไมต้อง Authentication?

**Cloud Models ต้อง API Key เพราะ:**
- 🌐 รันบน Ollama servers (ไม่ใช่ของคุณ)
- 💰 ต้องติดตาม usage
- 🔐 ต้องรักษา security
- ⚙️ ต้องจัดการ resources

**Local Models ไม่ต้อง เพราะ:**
- 💻 รันบนเครื่องของคุณ
- ⭕ ไม่มี server
- 🔒 ไม่ต้อง authenticate
- ⚡ เร็วกว่า

---

## 📞 ติดต่อความช่วยเหลือ

ถ้ายังใช้ไม่ได้ ให้:

1. รัน diagnostic:
```bash
python test_cloud_model.py
```

2. ดูข้อมูล error message

3. ลอง local model แทน:
```bash
ollama pull gemma2
# Edit: MODEL_TO_USE = "gemma2"
```

---

## 🎯 สรุป

**ตอนนี้คุณทำแล้ว:**
✅ `ollama signin` - ดี!

**ต้องทำต่อ:**
1. ตรวจสอบ token ตั้งค่าแล้ว: `echo $env:OLLAMA_API_KEY`
2. เริ่ม Ollama ใหม่: `ollama serve`
3. ทดสอบ: `python test_cloud_model.py`

ถ้ามีปัญหา ให้ลองใช้ local model (`gemma2`) แทน - ง่ายกว่าและเร็วกว่า!

