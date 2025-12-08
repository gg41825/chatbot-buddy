import requests
import logging
import traceback
from typing import Optional, Dict

from app.config import config
from app.services.scrapers import BaseScraper
from app.services.scrapers.ts_learn_german import TSLearnGermanScraper


# Scraper registry - add your custom scrapers here
SCRAPERS = {
    "ts_learn_german": TSLearnGermanScraper,
    # Add more scrapers here:
    # "bbc_news": BBCNewsScraper,
    # "cnn": CNNScraper,
}


def get_scraper() -> BaseScraper:
    """
    Factory function to get the configured scraper instance.

    Returns:
        Instance of BaseScraper based on configuration
    """
    # ConfigParser.get(section, option, fallback=default)
    scraper_type = config.get("news", "scraper.type", fallback="ts_learn_german")

    if scraper_type not in SCRAPERS:
        raise ValueError(f"Unknown scraper type: {scraper_type}. Available: {list(SCRAPERS.keys())}")

    scraper_class = SCRAPERS[scraper_type]

    # Initialize scraper with config parameters
    request_url = config["news"]["request.url"]

    return scraper_class(request_url=request_url)


def scrape_news() -> Optional[Dict[str, str]]:
    """
    Scrape news using the configured scraper.

    Returns:
        Dictionary with keys: 'title', 'link', 'content'
        None if scraping fails
    """
    scraper = get_scraper()
    return scraper.scrape()


def send_save_request(title, content):
    """Send request to save article to analyzer service"""
    data = {"title": title, "content": content}
    try:
        resp = requests.post(
            f"{config['analyzer']['host']}:{config['analyzer']['port']}{config['analyzer']['send.save.url']}",
            json=data,
        )
        logging.info(resp)
        return "OK"
    except Exception as e:
        logging.error(traceback.format_exc())
        return "error"


def send_generate_voca_request(title, content):
    """Send request to generate vocabularies from article"""
    data = {"title": title, "content": content}
    try:
        resp = requests.post(
            f"{config['analyzer']['host']}:{config['analyzer']['port']}{config['analyzer']['gen.voca.url']}",
            json=data,
        )
        return resp
    except Exception as e:
        logging.error(traceback.format_exc())
        return "error"
