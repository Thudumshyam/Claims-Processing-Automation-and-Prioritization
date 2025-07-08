import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pathlib import Path
import tempfile
import shutil
from app.document_processing import process_document
from app.info_extraction import extract_claim_info
from app.complexity_assessment import assess_complexity
from app.routing import route_claim
from app.auto_processing import auto_process_claim
from fastapi import Request
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claims Automation API")

@app.post("/process-claim/")
async def process_claim(file: UploadFile = File(...)):
    """
    Accepts a claim document, processes it through OCR, information extraction, complexity assessment, and routing.
    Returns extracted data, claim type, priority score, and routing status.
    """
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"
    logger.info(f"Received file: {filename}, type: {content_type}")
    # Save uploaded file to a temp location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")
    try:
        # 1. Document Processing
        text = process_document(tmp_path, str(content_type))
        if not text.strip():
            raise ValueError("No text could be extracted from the document.")
        # 2. Information Extraction
        claim_data = extract_claim_info(text)
        # 3. Complexity Assessment
        claim_type, priority_score = assess_complexity(claim_data)
        # 4. Routing
        routing_result = route_claim(claim_data, claim_type, priority_score)
        # 5. Auto-processing if simple
        if claim_type == "simple":
            auto_result = auto_process_claim(claim_data)
        else:
            auto_result = {"auto_processed": False}
        response = {
            "extracted_data": claim_data,
            "claim_type": claim_type,
            "priority_score": priority_score,
            **routing_result,
            **auto_result
        }
        logger.info(f"Pipeline result: {response}")
        return JSONResponse(content=response)
    except ValueError as ve:
        logger.error(f"User error: {ve}")
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error."})
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple HTML UI for uploading a claim document."""
    return """
    <html>
    <head>
        <title>Claims Automation UI</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', Arial, sans-serif;
                background: #f6f8fa;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 420px;
                margin: 60px auto;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 1.5px 4px rgba(0,0,0,0.04);
                padding: 32px 28px 24px 28px;
            }
            h2 {
                text-align: center;
                font-weight: 700;
                color: #2d3748;
                margin-bottom: 24px;
            }
            input[type="file"] {
                display: block;
                margin: 0 auto 18px auto;
                padding: 8px 0;
                font-size: 1rem;
                color: #2d3748;
            }
            button {
                display: block;
                width: 100%;
                background: linear-gradient(90deg, #4f8cff 0%, #2355d6 100%);
                color: #fff;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                padding: 12px 0;
                font-size: 1.1rem;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(79,140,255,0.08);
                transition: background 0.2s;
            }
            button:hover {
                background: linear-gradient(90deg, #2355d6 0%, #4f8cff 100%);
            }
            .result {
                background: #f4f8fb;
                padding: 18px 14px;
                margin-top: 28px;
                border-radius: 8px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.04);
                font-size: 1rem;
                color: #222;
                word-break: break-word;
                white-space: pre-wrap;
            }
            .result pre {
                margin: 0;
                font-size: 1rem;
                font-family: 'Roboto Mono', monospace, monospace;
                background: none;
                color: #2d3748;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Claims Automation</h2>
            <form id="upload-form" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.txt,.json,.csv,application/pdf,image/*,text/plain,application/json,text/csv,application/vnd.ms-excel" required>
                <button type="submit">Process Claim</button>
            </form>
            <div id="result" class="result" style="display:none;"></div>
        </div>
        <script>
        document.getElementById('upload-form').onsubmit = async function(e) {
            e.preventDefault();
            const form = e.target;
            const data = new FormData(form);
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'none';
            resultDiv.innerHTML = 'Processing...';
            try {
                const resp = await fetch('/process-claim/', {
                    method: 'POST',
                    body: data
                });
                let text = await resp.text();
                try {
                    const json = JSON.parse(text);
                    if (json.error) {
                        resultDiv.innerHTML = '<b style="color:red">' + json.error + '</b>';
                    } else {
                        resultDiv.innerHTML = '<pre>' + JSON.stringify(json, null, 2) + '</pre>';
                    }
                } catch (e) {
                    resultDiv.innerHTML = '<b style="color:red">' + text + '</b>';
                }
            } catch (err) {
                resultDiv.innerHTML = 'Error: ' + err;
            }
            resultDiv.style.display = 'block';
        };
        </script>
    </body>
    </html>
    """ 