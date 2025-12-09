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
    body = json.loads(body_str)

    try:
        signature = request.headers["X-Line-Signature"]
        linebot = LineBot()
        linebot.handler.handle(body_str, signature)

        # Get message text
        event = body["events"][0]
        if event["type"] != "message" or event["message"]["type"] != "text":
            return "OK"

        message_text = event["message"]["text"]
        reply_token = event["replyToken"]

        if GENERATE_VOCA in message_text:
            # Process German article
            response_text = process_german_article(message_text)
            linebot.reply(reply_token, response_text)
        else:
            # Fallback to normal analyzer behavior (AI bot)
            response_text = ask_question(message_text)
            linebot.reply(reply_token, response_text)
        return success_response(
            data={"response": response_text},
            message="Question answered successfully",
        )

    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your channel access token/channel secret.")
        return error_response("Invalid LINE signature", 400, "INVALID_LINE_SIGNATURE")
    except KeyError as e:
        logging.error(f"Missing key in webhook data: {str(e)}")
        return error_response(f"Missing required field: {str(e)}", 400, "MISSING_FIELD")
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response("Internal server error", 500, "INTERNAL_ERROR", details=str(e))

    return "OK"


@webhook_bp.route("/", methods=["GET"])
def home():
    return "Welcome to Ginny bot"
