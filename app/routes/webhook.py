from flask import Blueprint, request
import json
import logging
import traceback

from linebot.exceptions import InvalidSignatureError

from app.constants.line_request_constants import GENERATE_VOCA
from app.services.analyzer import process_german_article
from app.services.openai_service import ask_question
from app.services.line_bot import LineBot
from app.utils.response import success_response, error_response

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route("/callback", methods=["POST"])
def receive_message():
    """Handle LINE bot webhook callback"""
    body_str = request.get_data(as_text=True)
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in request body")
        return error_response("Invalid JSON", 400, "INVALID_JSON")

    try:
        signature = request.headers.get("X-Line-Signature")
        if not signature:
            return error_response("Missing LINE signature", 400, "MISSING_SIGNATURE")

        linebot = LineBot()
        linebot.handler.handle(body_str, signature)

        events = body.get("events", [])
        if not events:
            return "OK"

        event = events[0]
        if event.get("type") != "message" or event.get("message", {}).get("type") != "text":
            return "OK"

        message_text = event["message"]["text"]
        reply_token = event["replyToken"]

        if GENERATE_VOCA in message_text:
            response_text = process_german_article(message_text)
        else:
            response_text = ask_question(message_text)

        linebot.reply(reply_token, response_text)

    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your channel access token/channel secret.")
        return error_response("Invalid LINE signature", 400, "INVALID_LINE_SIGNATURE")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response("Internal server error", 500, "INTERNAL_ERROR", details=str(e))

    return success_response(
        data={"response": response_text},
        message="Question answered successfully",
    )


@webhook_bp.route("/", methods=["GET"])
def home():
    return "Welcome to Ginny bot"
