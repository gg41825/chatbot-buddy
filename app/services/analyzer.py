import logging
import traceback

from typing import List, Dict, Tuple
from app.models.database import Database
from app.services.openai_service import extract_vocabularies
from app.utils.response_format import format_vocabularies_for_line


def gen_and_save_vocabularies(text: str) -> Tuple[List[Dict], str]:
    """
    Generate and save vocabularies: extract vocabularies from article, save to DB

    Args:
        text: The German text

    Returns:
        vocabulary list, response message
    """
    try:
        logging.info("Processing text...")

        # Extract vocabularies using OpenAI
        vocabularies = extract_vocabularies(text, level="B2-C1", count=10)

        if not vocabularies:
            error_msg = "Sorry, I couldn't extract vocabularies from the article. Please make sure it's a German text."
            logging.warning(error_msg)
            return [], error_msg
        
        # Save vocabularies to database
        logging.info("Saving to DB...")
        db = Database()
        db.save_vocabularies(vocabularies)
        res_msg = f"Saved{len(vocabularies)} vocabularies"
        logging.info(res_msg)

        return vocabularies, res_msg

    except Exception as e:
        error_msg = f"Sorry, an error occurred while generating and save vocabularies: {str(e)}"
        logging.error(error_msg)
        return [], error_msg