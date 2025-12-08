import logging
import traceback

from flask import Blueprint

from app.services.line_bot import LineBot
from app.services.news_scraper import scrape_news
from app.utils.response import success_response, error_response

news_bp = Blueprint("news", __name__)


@news_bp.route("/pushnews", methods=["GET"])
def push_news():
    """Scrape news and push to LINE user."""
    try:
        news_data = scrape_news()

        if news_data is None:
            return error_response("Failed to scrape news", 500, "SCRAPE_FAILED")

        linebot = LineBot()
        linebot.send_message(news_data["title"], news_data["link"])

        return success_response(
            data={"message_sent": True, "title": news_data["title"]},
            message="News pushed successfully"
        )

    except ValueError as e:
        logging.error(f"ValueError: {str(e)}")
        return error_response(str(e), 400, "INVALID_CONFIG", details=str(e))
    except Exception as e:
        logging.error(traceback.format_exc())
        return error_response("Internal server error", 500, "INTERNAL_ERROR", details=str(e))
