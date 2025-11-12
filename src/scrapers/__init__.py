"""Web scrapers for free public tax resources"""

from .irs_scraper import IRSScraper
from .oecd_scraper import OECDScraper

__all__ = ["IRSScraper", "OECDScraper"]
