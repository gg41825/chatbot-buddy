from flask import jsonify
from typing import Any, Tuple, List, Dict

def success_response(data: Any = None, message: str = "Success") -> Tuple[Any, int]:
    """
    Generate a standardized success response.

    Args:
        data: The response data
        message: Success message

    Returns:
        Tuple of (JSON response, HTTP status code)
    """
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data

    return jsonify(response), 200


def error_response(
    message: str,
    status_code: int = 500,
    error_code: str = None,
    details: Any = None
) -> Tuple[Any, int]:
    """
    Generate a standardized error response.

    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
        details: Optional additional error details

    Returns:
        Tuple of (JSON response, HTTP status code)
    """
    response = {
        "success": False,
        "message": message,
    }

    if error_code:
        response["error_code"] = error_code

    if details is not None:
        response["details"] = details

    return jsonify(response), status_code

def format_vocabularies_for_line(vocabularies: List[Dict[str, str]]) -> str:
    """
    Format vocabularies list into a readable message for LINE.

    Args:
        vocabularies: List of vocabulary dictionaries

    Returns:
        Formatted string for LINE message
    """
    if not vocabularies:
        return "Sorry, I couldn't extract vocabularies from the text."

    message = f"Found {len(vocabularies)} German vocabularies:\n\n"

    for i, vocab in enumerate(vocabularies, 1):
        message += f"{i}. {vocab['german']}\n"
        message += f"{vocab['english']}\n"
        message += f"{vocab['chinese']}\n"
        if vocab.get('sentence'):
            # Truncate long sentences
            sentence = vocab['sentence']
            if len(sentence) > 100:
                sentence = sentence[:97] + "..."
            message += f"{sentence}\n"
        message += "\n"

    return message.strip()
