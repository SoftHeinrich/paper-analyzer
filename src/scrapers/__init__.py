"""
Scraper module initialization and registration.
"""

from .base import ScraperFactory
from .dblp_scraper import DBLPScraper
from .historical_dblp_scraper import HistoricalDBLPScraper
from .openreview_scraper import OpenReviewScraper
from .acl_scraper import ACLScraper

# Register all available scrapers
ScraperFactory.register_scraper('dblp', HistoricalDBLPScraper)  # Use historical scraper by default
ScraperFactory.register_scraper('dblp_basic', DBLPScraper)     # Keep basic scraper available
ScraperFactory.register_scraper('openreview', OpenReviewScraper)
ScraperFactory.register_scraper('anthology', ACLScraper)

__all__ = [
    'ScraperFactory',
    'DBLPScraper',
    'HistoricalDBLPScraper',
    'OpenReviewScraper',
    'ACLScraper'
]