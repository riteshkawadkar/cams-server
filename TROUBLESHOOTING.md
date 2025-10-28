# Troubleshooting Guide

## Common Errors and Solutions

### 1. PyCryptodome Error
**Error:** `PyCryptodome is required for AES algorithm`

**Solution:** 
- Added `pycryptodome==3.20.0` to requirements.txt
- Already fixed and deployed

### 2. Tabula Java Error
**Error:** `No JVM shared library file (libjvm.so) found`

**Solution:**
- Tabula requires Java, but Render free tier may not have it
- The parser has fallback methods (pdfplumber and PyPDF2)
- This is expected and handled by the code

### 3. pdfplumber Parsing Failed
**Possible causes:**
- PDF is corrupted
- PDF format not supported
- PDF requires password but wasn't provided

**Solution:**
- Try providing password parameter
- Check if PDF is encrypted
- Verify PDF file is valid

### 4. Password Not Working
**Error:** `password is invalid`

**Solution:**
- Ensure password is correct and case-sensitive
- Use the password exactly as provided
- Some PDFs may use owner password vs user password

---

## Dependencies

### Required for Encrypted PDFs
- `pycryptodome` - For AES encryption support
- `PyPDF2` - For password decryption

### Required for Table Extraction
- `tabula-py` - Requires Java (may not work on free tier)
- `pdfplumber` - Main parsing library

### Optional Dependencies
- `pytesseract` - OCR (if PDF contains images)
- `pandas` - Data manipulation
- `openpyxl` - Excel export

---

## Testing

### Test with unencrypted PDF
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "file=@statement.pdf"
```

### Test with encrypted PDF
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "file=@encrypted-statement.pdf" \
  -F "password=YOUR_PASSWORD"
```

---

## Deployment Status

Current issues fixed:
- ✅ Added pycryptodome for encrypted PDF support
- ✅ Updated build process
- ✅ Deployed to Render

Monitor: https://dashboard.render.com

