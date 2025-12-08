import logging

from app.models.database import Database
from app.services.openai_service import extract_vocabularies, format_vocabularies_for_line


def process_german_article(article_text: str) -> str:
    """
    Process German article: extract vocabularies, save to DB, and format response.

    Args:
        article_text: The German article text

    Returns:
        Formatted response message
    """
    try:
        logging.info("Processing German article...")

        # Extract vocabularies using OpenAI
        vocabularies = extract_vocabularies(article_text, level="B2-C1", count=10)

        if not vocabularies:
            return "Sorry, I couldn't extract vocabularies from the article. Please make sure it's a German text."

        # Generate title from first 50 characters of article
        title = article_text[:50].strip() + "..."

        # Save to database
        db = Database()
        article_id = db.save_article(title, article_text)

        # Save vocabularies
        db2 = Database()
        db2.save_vocabularies(article_id, vocabularies)

        logging.info(f"Saved article ID {article_id} with {len(vocabularies)} vocabularies")

        # Format response for LINE
        response = format_vocabularies_for_line(vocabularies)

        return response

    except Exception as e:
        logging.error(f"Error processing German article: {str(e)}")
        return f"Sorry, an error occurred while processing your article: {str(e)}"
