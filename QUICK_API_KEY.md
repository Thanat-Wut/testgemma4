# 🔑 API Key Setup - Quick Reference

## คำถาม: "set api key ยังไง?"

### ✅ คุณทำถูกแล้ว!
คุณรัน `ollama signin` ซึ่งเป็นวิธีที่ถูกต้องและง่ายที่สุด

---

## 📝 ขั้นตอนการตั้งค่า API Key

### ขั้นที่ 1: ลงชื่อ (✅ คุณทำแล้ว)
```bash
ollama signin
```
**ผลลัพธ์:**
- Ollama จะขอให้คุณสร้าง/ใช้บัญชี
- Token จะถูกบันทึกโดยอัตโนมัติ

### ขั้นที่ 2: ตรวจสอบ Token ถูกตั้งแล้ว (Optional)

**Windows PowerShell:**
```powershell
echo $env:OLLAMA_API_KEY
```

**Windows Command Prompt:**
```cmd
echo %OLLAMA_API_KEY%
```

**Expected output:** 
- ถ้าเห็นค่า (เช่น `abc123...`) = ✅ Token ready  
- ถ้าว่าง = Token อยู่ในไฟล์หรือระบบ (ยัง OK)

### ขั้นที่ 3: Restart Ollama (ถ้ากำลังรัน)
```bash
# Stop Ollama (Ctrl+C)
# Then restart
ollama serve
```

### ขั้นที่ 4: ทดสอบ Model
```bash
ollama list
# ควรแสดง: gemma4:31b-cloud
```

---

## 🧪 ทดสอบว่า API Key ทำงาน

```bash
python test_extraction.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
✓ Extracted invoice data via gemma4:31b-cloud:
  PO Number: PO-2024-001
  Company: ABC Corporation
  Grand Total: $60,000.00
```

**ถ้า 401 Unauthorized ยังเกิด:**
1. รัน `ollama signin` อีกครั้ง
2. Restart Ollama: `ollama serve`
3. Test ใหม่

---

## ⚡ Option: Manual Environment Variable (ถ้าต้องการ)

**Windows PowerShell:**
```powershell
# ดู key จากไฟล์ (ถ้า signin ไม่บันทึก)
$token = Get-Content $env:USERPROFILE\.ollama\auth.json | ConvertFrom-Json
$env:OLLAMA_API_KEY = $token.token

# ยืนยัน
echo $env:OLLAMA_API_KEY
```

**Linux/Mac:**
```bash
export OLLAMA_API_KEY=$(cat ~/.ollama/auth.json | jq -r '.token')
echo $OLLAMA_API_KEY
```

---

## 🎯 ผลลัพธ์

✅ **API Key Setup Complete!**
- Model: `gemma4:31b-cloud` ready
- Authentication: Configured
- App: Ready to use

```bash
python -m streamlit run app.py
```

---

## ❓ ถ้ายังไม่ได้

1. **ตรวจสอบ internet** - Cloud model ต้องเชื่อมกับ Ollama servers
2. **ตรวจสอบ Ollama version:** `ollama version` (ต้อง >= 0.21.0)
3. **ถ้ายังไม่ได้ ให้ใช้ local model แทน:**
   ```bash
   ollama pull gemma2
   # Edit line 21 ใน invoice_verification_agent.py:
   # MODEL_TO_USE = "gemma2"
   ```

---

## 📞 Summary

| ขั้นตอน | คำสั่ง | ผลลัพธ์ |
|--------|--------|--------|
| 1 | `ollama signin` | Token saved ✅ |
| 2 | `ollama list` | Shows gemma4:31b-cloud ✅ |
| 3 | `python test_extraction.py` | Model works ✅ |
| 4 | `streamlit run app.py` | App ready 🚀 |

**Done!** 🎉
