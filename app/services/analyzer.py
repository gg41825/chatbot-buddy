import logging
from typing import List, Dict, Tuple
from app.models.database import Database
from app.services.openai_service import extract_vocabularies, format_vocabularies_for_line


def process_german_article(text: str) -> Tuple[List[Dict], str]:
    """
    Process German article: extract vocabularies, save to DB, and format response.

    Args:
        text: The German text

    Returns:
        Formatted response message
    """
    try:
        logging.info("Processing German article...")

        # Extract vocabularies using OpenAI
        vocabularies = extract_vocabularies(text, level="B2-C1", count=10)

        if not vocabularies:
            return [], "Sorry, I couldn't extract vocabularies from the article. Please make sure it's a German text."

        # Save vocabularies to database
        db = Database()
        db.save_vocabularies(vocabularies)

        logging.info(f"Saved{len(vocabularies)} vocabularies")

        # Format response for LINE
        line_response = format_vocabularies_for_line(vocabularies)

        return vocabularies, line_response

    except Exception as e:
        logging.error(f"Error processing German article: {str(e)}")
        return [], f"Sorry, an error occurred while processing your article: {str(e)}"
