from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from app.config import config


class LineBot:
    def __init__(self):
        self.line_bot_api = LineBotApi(config["news"]["line.access.token"])
        self.handler = WebhookHandler(config["news"]["line.channel.secret"])

    def send_message(self, title, msg):
        """Send push message to user"""
        try:
            self.line_bot_api.push_message(
                config["news"]["line.user.id"],
                TextSendMessage(text=f"Your daily news: {title}\nLink: {msg}"),
            )
            return "OK"
        except:
            return "error"

    def reply(self, reply_token, text):
        """Reply to user message"""
        try:
            # can reply multiple messages
            self.line_bot_api.reply_message(
                reply_token=reply_token,
                messages=[TextSendMessage(text=text)]
            )
            return "OK"
        except:
            return "error"
