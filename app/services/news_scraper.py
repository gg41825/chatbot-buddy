from typing import Optional, Dict

from app import config
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
    scraper_type = config.NEWS_SCRAPER_TYPE

    if scraper_type not in SCRAPERS:
        raise ValueError(f"Unknown scraper type: {scraper_type}. Available: {list(SCRAPERS.keys())}")

    scraper_class = SCRAPERS[scraper_type]

    # Initialize scraper with config parameters
    request_url = config.NEWS_REQUEST_URL

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