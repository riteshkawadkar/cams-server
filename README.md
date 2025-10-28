# CAMS2CSV - Mutual Fund PDF Parser API

A FastAPI service for parsing CAMS mutual fund PDF statements and extracting holdings data.

## Features

- Parse CAMS mutual fund PDF statements
- Extract holdings data with detailed information
- Support for encrypted PDFs
- RESTful API with interactive documentation
- Export to JSON format

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn api:app --reload
```

3. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Deploy to Render.com (Recommended)

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/cams2csv.git
git push -u origin main
```

2. **Deploy on Render:**
   - Go to https://render.com
   - Sign up/Login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the configuration from `render.yaml`
   - Click "Create Web Service"
   - Your API will be live at: `https://your-service.onrender.com`

The `render.yaml` file is already configured for you!

### Alternative: Deploy to Ubuntu Server

**From Windows (PowerShell):**

```powershell
# Deploy files and start server
.\deploy_to_ubuntu.ps1
.\start_ubuntu_server.ps1
```

**From Linux:**

```bash
# Copy files to server
scp api.py mutual_fund_parser.py requirements.txt ubuntu@your-server:~/cams2csv/

# SSH into server and start
ssh ubuntu@your-server "cd ~/cams2csv && bash start_cams_server.sh"
```

## API Usage

### Parse PDF File

```python
import requests

# Upload and parse a PDF file
with open('statement.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/parse',
        files={'file': f}
    )
    data = response.json()
    print(data)
```

### Parse PDF from URL

```python
response = requests.post(
    'http://localhost:8000/parse',
    data={'url': 'https://example.com/statement.pdf'}
)
print(response.json())
```

### Parse Encrypted PDF

```python
with open('encrypted.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/parse',
        files={'file': f},
        data={'password': 'your-password'}
    )
```

## Response Format

```json
{
  "date": "2025-09-30",
  "portfolio_summary": {
    "total_schemes": 10,
    "total_valuation": 1500000.00,
    "total_investment": 1400000.00,
    "total_profit_loss": 100000.00,
    "overall_return_percentage": 7.14
  },
  "holdings": [
    {
      "scheme_name": "Fund Name",
      "isin": "INFXXX",
      "folio_no": "12345",
      "units": 1000.0,
      "nav": 15.50,
      "current_value": 15500.00,
      "cost": 15000.00,
      "profit_loss": 500.00
    }
  ]
}
```

## Server Management (Render.com)

With Render.com:
- ✅ Automatic HTTPS (SSL/TLS)
- ✅ Automatic deployments on git push
- ✅ Built-in logging
- ✅ Free tier available
- ✅ No firewall configuration needed

### View Logs (Render)
- Go to your service dashboard on Render
- Click "Logs" tab to view real-time logs

### Deploy Updates
```bash
git add .
git commit -m "Update code"
git push
# Render automatically deploys
```

## Project Structure

- `api.py` - FastAPI application
- `mutual_fund_parser.py` - PDF parsing logic
- `requirements.txt` - Python dependencies
- `render.yaml` - Render.com deployment configuration
- `Procfile` - Render.com process file
- `runtime.txt` - Python version specification

## Requirements

- Python 3.10+
- Java (for tabula-py)
- Required Python packages (see requirements.txt)

## License

MIT

