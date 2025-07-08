import logging
import pytest
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_process_claim_image(monkeypatch):
    """Test the /process-claim/ endpoint with a sample image file."""
    # Mock OCR and spaCy extraction for speed and determinism
    monkeypatch.setattr("app.document_processing.process_document", lambda path, t: "John Doe\n2023-01-01\n$12,000")
    monkeypatch.setattr("app.info_extraction.extract_claim_info", lambda text: {
        "claimant_name": "John Doe",
        "claim_date": "2023-01-01",
        "claim_amount": "$12,000"
    })
    test_file = Path(__file__).parent / "sample.jpg"
    # Create a dummy file if not exists
    if not test_file.exists():
        with open(test_file, "wb") as f:
            f.write(b"\x00\x01")
    with open(test_file, "rb") as f:
        response = client.post("/process-claim/", files={"file": ("sample.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Test response: {data}")
    assert data["claim_type"] == "complex"
    assert data["priority_score"] > 0
    assert "queued for human review" in data["routing_status"] 

def extract_claim_info(text: str) -> dict:
    # Try to extract using regex first
    name_match = re.search(r'Claimant[:\\s]+([A-Za-z ]+)', text)
    date_match = re.search(r'Date[:\\s]+([\\d-]+)', text)
    amount_match = re.search(r'Amount[:\\s\\$]+([\\d,\\.]+)', text)
    return {
        "claimant_name": name_match.group(1).strip() if name_match else None,
        "claim_date": date_match.group(1).strip() if date_match else None,
        "claim_amount": amount_match.group(1).strip() if amount_match else None
    } 