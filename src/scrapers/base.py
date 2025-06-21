"""
Base scraper architecture for paper information extraction.
"""

import time
import asyncio
import aiohttp
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

from src.models.paper import Paper, Author, ConferenceInfo
from config.conferences import SCRAPER_CONFIG


class BaseScraper(ABC):
    """Abstract base class for all paper scrapers."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        self.config = conference_config
        self.scraper_config = SCRAPER_CONFIG
        self.session = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def __enter__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.scraper_config['user_agent']
        })
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    @abstractmethod
    def scrape_papers(self, year: int, **kwargs) -> List[Paper]:
        """Scrape papers for a specific year."""
        pass
    
    @abstractmethod
    def scrape_conference_info(self, year: int) -> ConferenceInfo:
        """Scrape conference information for a specific year."""
        pass
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get a web page with error handling and rate limiting."""
        try:
            time.sleep(self.scraper_config['request_delay'])
            
            response = self.session.get(
                url,
                timeout=self.scraper_config['timeout'],
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def retry_request(self, func, *args, **kwargs):
        """Retry a request with exponential backoff."""
        max_retries = self.scraper_config['max_retries']
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                wait_time = (2 ** attempt) * self.scraper_config['request_delay']
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    def extract_authors(self, author_string: str) -> List[Author]:
        """Extract authors from a string representation."""
        if not author_string:
            return []
        
        authors = []
        # Simple parsing - can be enhanced for specific formats
        author_names = [name.strip() for name in author_string.split(',')]
        
        for name in author_names:
            if name:
                authors.append(Author(name=name))
        
        return authors


class AsyncBaseScraper(ABC):
    """Async version of base scraper for better performance."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        self.config = conference_config
        self.scraper_config = SCRAPER_CONFIG
        self.session = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=self.scraper_config['timeout'])
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.scraper_config['user_agent']}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def scrape_papers_async(self, year: int, **kwargs) -> List[Paper]:
        """Async version of scrape_papers."""
        pass
    
    async def get_page_async(self, url: str, **kwargs) -> Optional[str]:
        """Async version of get_page."""
        try:
            await asyncio.sleep(self.scraper_config['request_delay'])
            
            async with self.session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.text()
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def scrape_multiple_years(self, years: List[int]) -> Dict[int, List[Paper]]:
        """Scrape papers for multiple years concurrently."""
        tasks = [self.scrape_papers_async(year) for year in years]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        year_papers = {}
        for year, result in zip(years, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error scraping year {year}: {result}")
                year_papers[year] = []
            else:
                year_papers[year] = result
        
        return year_papers


class ScraperFactory:
    """Factory class for creating scrapers based on conference type."""
    
    _scrapers = {}
    
    @classmethod
    def register_scraper(cls, scraper_type: str, scraper_class):
        """Register a scraper class for a specific type."""
        cls._scrapers[scraper_type] = scraper_class
    
    @classmethod
    def create_scraper(cls, conference_config: Dict[str, Any]) -> BaseScraper:
        """Create a scraper instance based on conference configuration."""
        scraper_type = conference_config.get('type')
        
        if scraper_type not in cls._scrapers:
            raise ValueError(f"Unknown scraper type: {scraper_type}")
        
        scraper_class = cls._scrapers[scraper_type]
        return scraper_class(conference_config)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available scraper types."""
        return list(cls._scrapers.keys())