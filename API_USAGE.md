# CAMS2CSV API Usage Guide

## API Endpoint
**URL:** https://cams-server-rqxn.onrender.com/parse

## Request Methods

### cURL Commands

#### 1. Upload PDF without password (unencrypted PDFs)
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "file=@your-statement.pdf"
```

#### 2. Upload PDF with password (encrypted PDFs)
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "file=@your-statement.pdf" \
  -F "password=YOUR_PASSWORD"
```

#### 3. Parse PDF from URL without password
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "url=https://example.com/statement.pdf"
```

#### 4. Parse PDF from URL with password
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "url=https://example.com/statement.pdf" \
  -F "password=YOUR_PASSWORD"
```

#### 5. Save response to JSON file
```bash
curl -X POST "https://cams-server-rqxn.onrender.com/parse" \
  -F "file=@statement.pdf" \
  -F "password=YOUR_PASSWORD" \
  -o response.json
```

---

## PowerShell Commands

### 1. Upload PDF without password
```powershell
curl.exe -X POST "https://cams-server-rqxn.onrender.com/parse" `
  -F "file=@statement.pdf"
```

### 2. Upload PDF with password
```powershell
curl.exe -X POST "https://cams-server-rqxn.onrender.com/parse" `
  -F "file=@statement.pdf" `
  -F "password=BREPK5205M" `
  -o response.json
```

### 3. Parse from URL
```powershell
curl.exe -X POST "https://cams-server-rqxn.onrender.com/parse" `
  -F "url=https://example.com/statement.pdf" `
  -F "password=YOUR_PASSWORD"
```

---

## Python Examples

### Upload PDF without password
```python
import requests

with open('statement.pdf', 'rb') as f:
    response = requests.post(
        'https://cams-server-rqxn.onrender.com/parse',
        files={'file': f}
    )
print(response.json())
```

### Upload PDF with password
```python
import requests

with open('statement.pdf', 'rb') as f:
    response = requests.post(
        'https://cams-server-rqxn.onrender.com/parse',
        files={'file': f},
        data={'password': 'BREPK5205M'}
    )
print(response.json())
```

### Parse from URL with password
```python
import requests

response = requests.post(
    'https://cams-server-rqxn.onrender.com/parse',
    data={
        'url': 'https://example.com/statement.pdf',
        'password': 'BREPK5205M'
    }
)
print(response.json())
```

---

## JavaScript/Fetch Examples

### Upload PDF with password
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('password', 'YOUR_PASSWORD');

fetch('https://cams-server-rqxn.onrender.com/parse', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Parse from URL with password
```javascript
const formData = new FormData();
formData.append('url', 'https://example.com/statement.pdf');
formData.append('password', 'YOUR_PASSWORD');

fetch('https://cams-server-rqxn.onrender.com/parse', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Response Format

```json
{
  "date": "2025-10-28",
  "portfolio_summary": {
    "total_schemes": 12,
    "total_valuation": 16747917.83,
    "total_investment": 15987970.62,
    "total_profit_loss": 1759947.21,
    "overall_return_percentage": 12.69
  },
  "holdings": [
    {
      "scheme_name": "Fund Name",
      "isin": "INF123ABC456",
      "folio_no": "12345",
      "arn_code": "ARN-77893",
      "units": 1000.0,
      "nav": 15.50,
      "cost": 15000.0,
      "current_value": 15500.0,
      "ter_regular": 1.5,
      "ter_direct": 1.2,
      "commission": 100.0,
      "profit_loss": 500.0,
      "profit_loss_percentage": 3.33
    }
  ]
}
```

---

## Important Notes

1. **Password is optional** - Only provide it if your PDF is encrypted
2. **File OR URL required** - You must provide either a file upload or a URL
3. **Case-sensitive password** - Make sure to enter the exact password
4. **Response format** - Always returns JSON with portfolio summary and holdings array

---

## Testing the API

### Using cURL
```bash
curl https://cams-server-rqxn.onrender.com/docs
```

### Using Browser
Open: https://cams-server-rqxn.onrender.com/docs

---

## Common Errors

| Error | Solution |
|-------|----------|
| `Provide either a PDF file upload or a URL` | Include either `file` or `url` parameter |
| `Failed to download URL` | Check if URL is publicly accessible |
| `No holdings data parsed from PDF` | PDF format may not be supported |
| `password is invalid` | Check if password is correct and case-sensitive |

