import logging
from typing import List
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import tempfile
import json as js
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_image(image: Image.Image) -> str:
    """Extract text from a PIL Image using Tesseract OCR."""
    logger.info("Extracting text from image using OCR.")
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Convert PDF pages to images and extract text from each page."""
    logger.info(f"Extracting text from PDF: {pdf_path}")
    text = ""
    images = convert_from_path(str(pdf_path))
    for i, image in enumerate(images):
        logger.info(f"Processing page {i+1} of PDF.")
        text += extract_text_from_image(image) + "\n"
    return text

def extract_text_from_txt(txt_path: Path) -> str:
    """Read text from a .txt file."""
    logger.info(f"Extracting text from TXT: {txt_path}")
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text_from_json(json_path: Path) -> str:
    """Extract text from a JSON file by flattening its content."""
    logger.info(f"Extracting text from JSON: {json_path}")
    with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
        try:
            data = js.load(f)
            def flatten(d):
                if isinstance(d, dict):
                    return ' '.join([flatten(v) for v in d.values()])
                elif isinstance(d, list):
                    return ' '.join([flatten(i) for i in d])
                else:
                    return str(d)
            return flatten(data)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Invalid JSON file.")

def extract_text_from_csv(csv_path: Path) -> str:
    """Extract text from a CSV file by joining all cells."""
    logger.info(f"Extracting text from CSV: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        return '\n'.join([' '.join(row) for row in reader])

def process_document(file_path: Path, file_type: str) -> str:
    """
    Process an uploaded document (PDF, image, txt, json, csv) and extract text.
    Raises ValueError for unsupported or empty files.
    """
    logger.info(f"Processing document: {file_path}, type: {file_type}")
    if file_path.stat().st_size == 0:
        logger.error("Uploaded file is empty.")
        raise ValueError("Uploaded file is empty.")
    ext = file_path.suffix.lower()
    try:
        if file_type.lower() == 'application/pdf' or ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_type.lower().startswith('image/') or ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            image = Image.open(file_path)
            return extract_text_from_image(image)
        elif file_type.lower() == 'text/plain' or ext == '.txt':
            return extract_text_from_txt(file_path)
        elif file_type.lower() == 'application/json' or ext == '.json':
            return extract_text_from_json(file_path)
        elif file_type.lower() in ['text/csv', 'application/vnd.ms-excel'] or ext == '.csv':
            return extract_text_from_csv(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type} (.{ext})")
            raise ValueError(f"Unsupported file type: {file_type} (.{ext})")
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise ValueError(f"Error processing document: {e}") 