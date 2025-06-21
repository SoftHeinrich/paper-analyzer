"""
DBLP scraper for conferences indexed in DBLP database.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .base import BaseScraper
from src.models.paper import Paper, Author, ConferenceInfo
from config.conferences import DBLP_CONFIG


class DBLPScraper(BaseScraper):
    """Scraper for DBLP database."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        super().__init__(conference_config)
        self.dblp_config = DBLP_CONFIG
        
    def scrape_papers(self, year: int, **kwargs) -> List[Paper]:
        """Scrape papers from DBLP for a specific year."""
        venue_path = self.config.get('venue_path', 'conf/icse')
        venue_short = self.config.get('venue_short', 'icse')
        xml_url = self.dblp_config['xml_url'].format(venue_path=venue_path, venue_short=venue_short, year=year)
        
        response = self.get_page(xml_url)
        if not response:
            self.logger.warning(f"Could not fetch DBLP data for {venue_short} {year}")
            return []
        
        return self._parse_dblp_xml(response.text, year)
    
    def scrape_conference_info(self, year: int) -> ConferenceInfo:
        """Scrape conference information from DBLP."""
        papers = self.scrape_papers(year)
        
        conference_info = ConferenceInfo(
            name=self.config['name'],
            acronym=self.config.get('acronym', ''),
            year=year,
            papers=papers
        )
        
        return conference_info
    
    def _parse_dblp_xml(self, xml_content: str, year: int) -> List[Paper]:
        """Parse DBLP XML content to extract papers."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for entry in root.findall('.//inproceedings'):
                paper = self._parse_paper_entry(entry, year)
                if paper:
                    papers.append(paper)
                    
        except ET.ParseError as e:
            self.logger.error(f"Error parsing DBLP XML: {e}")
        
        return papers
    
    def _parse_paper_entry(self, entry: ET.Element, year: int) -> Optional[Paper]:
        """Parse a single paper entry from DBLP XML."""
        try:
            title_elem = entry.find('title')
            if title_elem is None:
                return None
            
            title = self.clean_text(title_elem.text or '')
            if not title:
                return None
            
            # Extract authors
            authors = []
            for author_elem in entry.findall('author'):
                if author_elem.text:
                    authors.append(Author(name=self.clean_text(author_elem.text)))
            
            # Extract other information
            pages_elem = entry.find('pages')
            pages = pages_elem.text if pages_elem is not None else None
            
            doi_elem = entry.find('doi')
            doi = doi_elem.text if doi_elem is not None else None
            
            url_elem = entry.find('url')
            url = url_elem.text if url_elem is not None else None
            
            # Generate DBLP URL if not present
            if not url and entry.get('key'):
                url = f"https://dblp.org/rec/{entry.get('key')}"
            
            # Extract track type if conference supports it
            track_type = self._extract_track_type(title, entry)
            
            paper = Paper(
                title=title,
                authors=authors,
                year=year,
                venue=self.config.get('name', ''),
                venue_type='conference',
                track_type=track_type,
                pages=pages,
                doi=doi,
                url=url,
                metadata={'dblp_key': entry.get('key')}
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing paper entry: {e}")
            return None
    
    def _extract_track_type(self, title: str, entry: ET.Element) -> Optional[str]:
        """Extract track type for conferences that support it."""
        # Check if this conference tracks presentation types
        track_types = self.config.get('track_types', [])
        if not track_types:
            return None
        
        # For ICLR and similar conferences, track info might be in DBLP key or title
        dblp_key = entry.get('key', '')
        
        # Some DBLP entries include track in the key (e.g., conf/iclr/2023-oral)
        for track in track_types:
            if track.lower() in dblp_key.lower():
                return track
            if track.lower() in title.lower():
                return track
        
        # Default to poster for conferences that have track types but no specific indicator
        return 'poster'
    
    def search_papers(self, query: str, max_results: int = 100) -> List[Paper]:
        """Search for papers using DBLP API."""
        search_url = f"{self.dblp_config['base_url']}"
        params = {
            'q': query,
            'format': 'xml',
            'h': max_results
        }
        
        response = self.get_page(search_url, params=params)
        if not response:
            return []
        
        return self._parse_search_results(response.text)
    
    def _parse_search_results(self, xml_content: str) -> List[Paper]:
        """Parse DBLP search results."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for hit in root.findall('.//hit'):
                info = hit.find('info')
                if info is None:
                    continue
                
                title_elem = info.find('title')
                if title_elem is None:
                    continue
                
                title = self.clean_text(title_elem.text or '')
                if not title:
                    continue
                
                authors = []
                for author_elem in info.findall('authors/author'):
                    if author_elem.text:
                        authors.append(Author(name=self.clean_text(author_elem.text)))
                
                year_elem = info.find('year')
                year = int(year_elem.text) if year_elem is not None and year_elem.text else None
                
                venue_elem = info.find('venue')
                venue = venue_elem.text if venue_elem is not None else None
                
                doi_elem = info.find('doi')
                doi = doi_elem.text if doi_elem is not None else None
                
                url_elem = info.find('url')
                url = url_elem.text if url_elem is not None else None
                
                paper = Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    venue=venue,
                    doi=doi,
                    url=url
                )
                
                papers.append(paper)
                
        except ET.ParseError as e:
            self.logger.error(f"Error parsing DBLP search results: {e}")
        
        return papers