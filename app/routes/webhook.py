from flask import Blueprint, request
import json
import logging
import traceback

from linebot.exceptions import InvalidSignatureError

from app.constants.line_request_constants import GENERATE_VOCA
from app.services.openai_service import ask_question, extract_vocabularies
from app.services.line_bot import LineBot
from app.utils.response_format import success_response, error_response, format_vocabularies_for_line
webhook_bp = Blueprint('webhook', __name__)

def handle_line_message(message_text: str) -> str:
    "Based on the message content, decide whether to ask a question or generate voca list"
    
    if GENERATE_VOCA in message_text:
        vocabularies_data = extract_vocabularies(message_text)
        response_text = format_vocabularies_for_line(vocabularies_data)
        
    else:
        response_text = ask_question(message_text) 

    if not isinstance(response_text, str):
        error_msg = f"Business logic returned non-string type: {type(response_text)}"
        logging.error(error_msg)
        return "Internal service error: Invalid response format."
    
    return response_text

@webhook_bp.route("/callback", methods=["POST"])
def receive_message():
    """Handle LINE bot webhook callback"""
    body_str = request.get_data(as_text=True)
    
    # Init token and text
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
        
        if not events:
            return "OK"
        
        # Usually, only one reply is needed, so just returned it
        # For non-text messages, continue looping or end directly, returning "OK" in the end
        for event in events:
            if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
                
                message_text = event["message"]["text"]
                reply_token = event["replyToken"]
                response_text = handle_line_message(message_text)
                linebot.reply(reply_token, response_text)
                
                return success_response(
                    data={"response": response_text},
                    message="Question answered successfully",
                )

    except InvalidSignatureError:
        error_msg = "Invalid signature. Please check your channel access token/channel secret."
        logging.error(error_msg)
        return error_response(error_msg, 400, "INVALID_LINE_SIGNATURE")
        
    except json.JSONDecodeError:
        error_msg = "Invalid JSON in request body"
        logging.error(error_msg)
        return error_response(error_msg, 400, "INVALID_JSON")

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Internal server error processing LINE message: {error_trace}")
        
        if reply_token:
            error_user_message = "An internal error has occurred. Please try again later."
            try:
                linebot.reply(reply_token, error_user_message)
            except Exception as reply_error:
                logging.error(f"Failed to send error reply: {reply_error}")
            
        return error_response(
            "Internal server error", 
            500, 
            "INTERNAL_ERROR", 
            details=f"See logs for traceback. Exception: {str(e)}"
        )
    return "OK"


@webhook_bp.route("/", methods=["GET"])
def home():
    return "Welcome to Ginny bot"
