import logging
import traceback

from flask import Blueprint, request

from app.services.openai_service import ask_question
from app.services.analyzer import gen_and_save_vocabularies

from app.utils.response_format import success_response, error_response

analyzer_bp = Blueprint("analyzer", __name__)


# For directly accessing Bot for asking questions
@analyzer_bp.route("/ask_bot", methods=["POST"])
def get_article():
    try:
        body = request.get_json()
        if not body:
            return error_response("Invalid JSON payload", 400, "INVALID_JSON")

        if not body["text"]:
            return error_response("Missing article text", 400, "MISSING_CONTENT")

        text = body["text"]
        if not text:
            return error_response("Missing 'text' field", 400, "MISSING_TEXT")

        analyzer_signature = request.headers.get("Analyzer-Signature")
        if not analyzer_signature:
            logging.error("Missing signature headers")
            return error_response("Missing signature headers", 401, "MISSING_SIGNATURE")

        messages = [{"role": "user", "content": text}]

        # Call GPT
        gpt_result = ask_question(messages)

        if not gpt_result or "choices" not in gpt_result:
            logging.error("Invalid response from OpenAI")
            return error_response("Failed to get response from AI", 500, "AI_ERROR")

        return success_response(
            data={"response": gpt_result["choices"][0]["message"]["content"]},
            message="Question answered successfully",
        )

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return error_response(f"Missing required field: {str(e)}", 400, "MISSING_FIELD")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response(
            "Internal server error", 500, "INTERNAL_ERROR", details=str(e)
        )
    

# For directly accessing Bot for generating vocabularies
@analyzer_bp.route("/gen_voca", methods=["POST"])
def generate_voca():
    try:
        body = request.get_json()
        if not body:
            return error_response("Invalid JSON payload", 400, "INVALID_JSON")

        if not body["text"]:
            return error_response("Missing article text", 400, "MISSING_CONTENT")
        text = body["text"]

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
            logging.error("Missing signature headers")
            return error_response("Missing signature headers", 401, "MISSING_SIGNATURE")

        # Use extract_vocabularies to get structured vocabulary data
        vocabularies, _ = gen_and_save_vocabularies(text)

        if not vocabularies:
            logging.error("Failed to extract vocabularies")
            return error_response("Failed to generate vocabularies", 500, "AI_ERROR")

        return success_response(
            data={
                "vocabularies": vocabularies,
                "count": len(vocabularies),
            },
            message="Vocabularies generated successfully",
        )

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return error_response(f"Missing required field: {str(e)}", 400, "MISSING_FIELD")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response(
            "Internal server error", 500, "INTERNAL_ERROR", details=str(e)
        )


@analyzer_bp.route("/", methods=["GET"])
def home():
    return "Welcome to Ginny's Analyzer"
