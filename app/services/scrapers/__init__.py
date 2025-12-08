from abc import ABC, abstractmethod
from typing import Optional, Dict


class BaseScraper(ABC):
    """Abstract base class for news scrapers"""

    @abstractmethod
    def scrape(self) -> Optional[Dict[str, str]]:
        """
        Scrape news from the source.

        Returns:
            Dictionary with keys: 'title', 'link', 'content'
            None if scraping fails
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this scraper"""
        pass
