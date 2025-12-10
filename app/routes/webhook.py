from flask import Blueprint, request
import json
import logging
import traceback

from linebot.exceptions import InvalidSignatureError

from app.constants.line_request_constants import GENERATE_VOCA
from app.services.analyzer import gen_and_save_vocabularies
from app.services.openai_service import ask_question
from app.services.line_bot import LineBot
from app.utils.response_format import success_response, error_response

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route("/callback", methods=["POST"])
def receive_message():
    """Handle LINE bot webhook callback"""
    body_str = request.get_data(as_text=True)
    
    # Init token
    reply_token = None
    response_text = None 
    
    try:
        signature = request.headers.get("X-Line-Signature")
        if not signature:
            return error_response("Missing LINE signature", 400, "MISSING_SIGNATURE")

        linebot = LineBot()
        linebot.handler.handle(body_str, signature)

        body = json.loads(body_str)
        events = body.get("events", [])
        
        # LINE Webhook cound send multiple events at a time
        for event in events:
            # Need to deal with this request only when there is message.text
            if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
                
                message_text = event["message"]["text"]
                reply_token = event["replyToken"]
                
                if GENERATE_VOCA in message_text:
                    _, response_text = gen_and_save_vocabularies(message_text)
                else:
                    response_text = ask_question(message_text) 

                # Make sure that response_text is string
                if not isinstance(response_text, str):
                    logging.error(f"Function returned non-string: {type(response_text)}")
                    response_text = "Internal error: Invalid service response format"
                
                # Usually, only one reply is needed, so just returned it
                linebot.reply(reply_token, response_text)
                
                return success_response(
                    data={"response": response_text},
                    message="Question answered successfully",
                )

    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your channel access token/channel secret.")
        return error_response("Invalid LINE signature", 400, "INVALID_LINE_SIGNATURE")
        
    except json.JSONDecodeError:
        logging.error("Invalid JSON in request body")
        return error_response("Invalid JSON", 400, "INVALID_JSON")

    except Exception as e:
        logging.error(traceback.format_exc())
        
        if reply_token:
            error_user_message = "An internal error has occurred. Please try again later."
            try:
                linebot.reply(reply_token, error_user_message)
            except Exception as reply_error:
                logging.error(f"Failed to send error reply: {reply_error}")
            
        return error_response("Internal server error", 500, "INTERNAL_ERROR", details=str(e))

    # No events to process (e.g., an empty events list), or if a non-text message has been processed
    return "OK"


@webhook_bp.route("/", methods=["GET"])
def home():
    return "Welcome to Ginny bot"
