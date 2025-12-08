from flask import jsonify
from typing import Any, Tuple


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
