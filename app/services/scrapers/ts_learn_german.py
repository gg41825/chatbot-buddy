import requests
import logging
import traceback
from bs4 import BeautifulSoup
from typing import Optional, Dict

from app.services.scrapers import BaseScraper


class TSLearnGermanScraper(BaseScraper):
    """
    Example scraper for Tagesschau German news articles.
    This is a reference implementation showing the expected HTML structure.

    Example configuration:
        request.url = https://www.tagesschau.de/wissen
    """

    def __init__(self, request_url: str):
        """
        Args:
            request_url: Full URL to fetch the news list (e.g., "https://www.tagesschau.de/wissen")
        """
        self.request_url = request_url

    def scrape(self) -> Optional[Dict[str, str]]:
        """Scrape news from Tagesschau"""
        try:
            # Fetch the news list page
            resp = requests.get(self.request_url)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Find the first article link and title
            news_link = soup.find("a", class_="teaser__link").get("href")
            news_title = (
                soup.find("a", class_="teaser__link")
                .select_one(".teaser__headline")
                .text
            )

            # Construct full article URL - assuming links are relative paths
            news_link = self.request_url.rsplit('/', 1)[0] + news_link

            resp = requests.get(news_link)

            # Extract article content paragraphs
            paragraphs = []
            soup = BeautifulSoup(resp.text, "html.parser")
            for paragraph in soup.find_all("p", class_="textabsatz"):
                paragraphs.append(paragraph.get_text())

            return {
                "title": news_title,
                "link": news_link,
                "content": "\n".join(paragraphs).strip()
            }
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def get_name(self) -> str:
        return "Tagesschau Learn German"
