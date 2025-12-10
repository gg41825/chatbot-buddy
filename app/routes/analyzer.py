import logging
import traceback
import os

from flask import Blueprint, request, jsonify
from functools import wraps

from app.services.openai_service import ask_question
from app.services.analyzer import gen_and_save_vocabularies

from app.utils.response_format import success_response, error_response

analyzer_bp = Blueprint("analyzer", __name__)

# Read the switch status from env var. Default is False; Only enabled when set to "TRUE" (case-insensitive).
FEATURE_ANALYZER_ENABLED = os.getenv("FEATURE_ANALYZER_ENABLED", "False").upper() == "TRUE"
def feature_flag_check(f):
    """
   Check the FEATURE_ANALYZER_ENABLED env var; if False, return a 404 error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not FEATURE_ANALYZER_ENABLED:
            error_msg = f"Route {request.path} is currently disabled by feature flag."
            logging.warning(error_msg)
            return error_response(error_msg, 404, "ROUTE_DISABLED")
        return f(*args, **kwargs)
    return decorated_function

# For directly accessing Bot for asking questions
@analyzer_bp.route("/ask_bot", methods=["POST"])
@feature_flag_check
def get_article():
    try:
        body = request.get_json()
        if not body:
            return error_response("Invalid JSON payload", 400, "INVALID_JSON")

        text = body.get("text")
        if not text:
            return error_response("Missing 'text' field", 400, "MISSING_TEXT")

        analyzer_signature = request.headers.get("Analyzer-Signature")
        if not analyzer_signature:
            error_msg = "Missing signature headers"
            logging.error(error_msg)
            return error_response(error_msg, 401, "MISSING_SIGNATURE")

        messages = [{"role": "user", "content": text}]

        # Call GPT
        gpt_result = ask_question(messages)

        if not gpt_result or "choices" not in gpt_result:
            error_msg = "Invalid response from OpenAI"
            logging.error(error_msg)
            return error_response(error_msg, 500, "AI_ERROR")

        return success_response(
            data={"response": gpt_result["choices"][0]["message"]["content"]},
            message="Question answered successfully",
        )

    except KeyError as e:
        error_msg = f"Missing key: {str(e)}"
        logging.error(error_msg)
        return error_response(error_msg, 400, "MISSING_FIELD")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response(
            "Internal server error", 500, "INTERNAL_ERROR", details=str(e)
        )
    

# For directly accessing Bot for generating vocabularies
@analyzer_bp.route("/gen_voca", methods=["POST"])
@feature_flag_check
def generate_voca():
    try:
        body = request.get_json()
        if not body:
            return error_response("Invalid JSON payload", 400, "INVALID_JSON")

        text = body.get("text")
        if not text:
            return error_response("Missing 'text' field", 400, "MISSING_TEXT")

        # Validate minimum word count (at least 10 words)
        word_count = len(text.split())
        if word_count < 10:
            return error_response(
                f"Article too short. Need at least 10 words, got {word_count}",
                400,
                "TEXT_TOO_SHORT",
            )

        analyzer_signature = request.headers.get("Analyzer-Signature")
        if not analyzer_signature:
            error_msg = "Missing signature headers"
            logging.error(error_msg)
            return error_response(error_msg, 401, "MISSING_SIGNATURE")

        # Use extract_vocabularies to get structured vocabulary data
        vocabularies, resp_msg = gen_and_save_vocabularies(text)
        if not vocabularies:
            return error_response(resp_msg, 500, "AI_ERROR")

        return success_response(
            data={
                "vocabularies": vocabularies,
                "count": len(vocabularies),
            },
            message=resp_msg,
        )

    except KeyError as e:
        error_msg = f"Missing key: {str(e)}"
        logging.error(error_msg)
        return error_response(error_msg, 400, "MISSING_FIELD")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response(
            "Internal server error", 500, "INTERNAL_ERROR", details=str(e)
        )


@analyzer_bp.route("/", methods=["GET"])
@feature_flag_check
def home():
    return "Welcome to Ginny's Analyzer"
