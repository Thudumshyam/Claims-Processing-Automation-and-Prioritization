import logging
from typing import Dict, Any, Tuple
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_amount(amount_str: str) -> float:
    """Parse a string representing money and return a float value."""
    if not amount_str:
        return 0.0
    # Remove currency symbols and commas
    amount = re.sub(r'[^\d.]', '', amount_str)
    try:
        return float(amount)
    except ValueError:
        logger.warning(f"Could not parse amount: {amount_str}")
        return 0.0

def assess_complexity(claim_data: Dict[str, Any]) -> Tuple[str, int]:
    """Classify claim as simple or complex and assign a priority score if complex."""
    logger.info("Assessing claim complexity.")
    required_fields = ["claimant_name", "claim_date", "claim_amount"]
    missing_fields = [f for f in required_fields if not claim_data.get(f)]
    amount = parse_amount(claim_data.get("claim_amount", ""))
    if missing_fields or amount > 10000:
        claim_type = "complex"
        # Priority score: more missing fields and higher amount = higher priority
        priority_score = 50 + 10 * len(missing_fields) + int(amount // 1000)
    else:
        claim_type = "simple"
        priority_score = 0
    logger.info(f"Claim type: {claim_type}, Priority score: {priority_score}")
    return claim_type, priority_score 