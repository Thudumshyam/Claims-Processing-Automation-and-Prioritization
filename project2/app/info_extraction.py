import logging
from typing import Dict, Any
import spacy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model globally
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    raise

def extract_claim_info(text: str) -> Dict[str, Any]:
    """Extract claimant name, claim date, and claim amount from text using spaCy NER."""
    logger.info("Extracting claim information using spaCy NER.")
    doc = nlp(text)
    claimant_name = None
    claim_date = None
    claim_amount = None
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not claimant_name:
            claimant_name = ent.text
        elif ent.label_ == "DATE" and not claim_date:
            claim_date = ent.text
        elif ent.label_ == "MONEY" and not claim_amount:
            claim_amount = ent.text
    logger.info(f"Extracted - Name: {claimant_name}, Date: {claim_date}, Amount: {claim_amount}")
    return {
        "claimant_name": claimant_name,
        "claim_date": claim_date,
        "claim_amount": claim_amount
    } 