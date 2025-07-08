import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulated human review queue
human_review_queue = []

def route_claim(claim_data: Dict[str, Any], claim_type: str, priority_score: int) -> Dict[str, Any]:
    """Route claim to auto-processing or human review queue based on type and priority."""
    logger.info(f"Routing claim. Type: {claim_type}, Priority: {priority_score}")
    if claim_type == "simple":
        status = "auto-processed"
    else:
        # Add to human review queue (ordered by priority)
        human_review_queue.append((priority_score, claim_data))
        human_review_queue.sort(reverse=True, key=lambda x: x[0])
        status = f"queued for human review (priority {priority_score})"
    logger.info(f"Routing status: {status}")
    return {"routing_status": status} 