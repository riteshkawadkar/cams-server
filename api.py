from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import requests
from mutual_fund_parser import MutualFundDataParser

app = FastAPI(title="CAMS PDF Parser API")


@app.post("/parse")
async def parse_pdf(file: UploadFile = File(None), url: str = Form(None), password: str = Form(None)):
    """Parse a CAMS/PDF holding statement and return JSON.

    Provide either a file upload (multipart/form-data) or a publicly-accessible `url`.
    An optional `password` form field may be provided if the PDF is encrypted.
    """
    if file is None and not url:
        raise HTTPException(status_code=400, detail="Provide either a PDF file upload or a URL")

    temp_path = None
    try:
        # Download or save uploaded file to a temporary file
        if url:
            try:
                resp = requests.get(url, stream=True, timeout=20)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to download URL: {e}")
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download URL: status {resp.status_code}")

            fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            with open(temp_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            contents = await file.read()
            fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            with open(temp_path, 'wb') as f:
                f.write(contents)

        parser = MutualFundDataParser()
        # parse_from_pdf accepts an optional password
        df = parser.parse_from_pdf(temp_path, password=password) if password else parser.parse_from_pdf(temp_path)

        if df is None or df.empty:
            return JSONResponse(status_code=422, content={"error": "No holdings data parsed from PDF"})

        json_data = parser.to_json_dict(df)
        return JSONResponse(content=json_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
