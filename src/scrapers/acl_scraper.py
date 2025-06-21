"""
ACL Anthology scraper for NLP conferences.
"""

import json
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .base import BaseScraper
from src.models.paper import Paper, Author, ConferenceInfo
from config.conferences import ACL_ANTHOLOGY_CONFIG


class ACLScraper(BaseScraper):
    """Scraper for ACL Anthology."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        super().__init__(conference_config)
        self.acl_config = ACL_ANTHOLOGY_CONFIG
        
    def scrape_papers(self, year: int, **kwargs) -> List[Paper]:
        """Scrape papers from ACL Anthology for a specific year."""
        venue_name = self.config.get('venue_short', self.config['venue_key'].split('/')[-1])
        
        # ACL Anthology uses events/venue-year format
        anthology_url = f"{self.acl_config['base_url']}/events/{venue_name}-{year}/"
        
        response = self.get_page(anthology_url)
        if not response:
            self.logger.warning(f"Could not fetch ACL Anthology page for {venue_name} {year}")
            return []
        
        soup = self.parse_html(response.text)
        return self._parse_anthology_page(soup, year)
    
    def scrape_conference_info(self, year: int) -> ConferenceInfo:
        """Scrape conference information from ACL Anthology."""
        papers = self.scrape_papers(year)
        
        conference_info = ConferenceInfo(
            name=self.config['name'],
            acronym=self.config.get('venue_key', '').upper(),
            year=year,
            papers=papers
        )
        
        return conference_info
    
    def _parse_anthology_page(self, soup, year: int) -> List[Paper]:
        """Parse ACL Anthology page to extract papers."""
        papers = []
        
        # Look for paper entries in the anthology page
        paper_entries = soup.find_all('p', class_='d-sm-flex align-items-stretch')
        
        for entry in paper_entries:
            paper = self._parse_paper_entry(entry, year)
            if paper:
                papers.append(paper)
        
        return papers
    
    def _parse_paper_entry(self, entry, year: int) -> Optional[Paper]:
        """Parse a single paper entry from ACL Anthology."""
        try:
            # Extract title
            title_elem = entry.find('strong')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            if title_link:
                title = self.clean_text(title_link.text)
                paper_url = urljoin(self.acl_config['base_url'], title_link.get('href', ''))
            else:
                title = self.clean_text(title_elem.text)
                paper_url = None
            
            if not title:
                return None
            
            # Filter for main track papers only (long and short papers)
            if paper_url:
                # Extract paper ID from URL to check track
                paper_id = paper_url.rstrip('/').split('/')[-1].replace('.html', '')
                if paper_id and '.' in paper_id and '-' in paper_id:
                    parts = paper_id.split('-')
                    if len(parts) >= 2:
                        track = parts[1].split('.')[0]
                        # Different conferences use different track names for main track
                        main_tracks = ['long', 'short', 'main']
                        if track not in main_tracks:
                            # Skip non-main track papers
                            return None
            
            # Extract authors
            authors = []
            author_spans = entry.find_all('a', href=lambda x: x and '/people/' in x)
            
            for author_link in author_spans:
                author_name = self.clean_text(author_link.text)
                if author_name:
                    authors.append(Author(name=author_name))
            
            # Extract paper ID and generate URLs
            paper_id = None
            if paper_url:
                paper_id = paper_url.split('/')[-1].replace('.html', '')
            
            pdf_url = None
            bibtex_url = None
            if paper_id:
                pdf_url = f"{self.acl_config['base_url']}/{paper_id}.pdf"
                bibtex_url = f"{self.acl_config['api_base']}/{paper_id}"
            
            # Extract abstract if available (would need to fetch individual paper page)
            abstract = None
            
            # Extract pages if available
            pages = None
            pages_text = entry.get_text()
            if 'pages' in pages_text.lower():
                # Try to extract page numbers using regex or text parsing
                import re
                page_match = re.search(r'pages?\s*(\d+[-–]\d+)', pages_text, re.IGNORECASE)
                if page_match:
                    pages = page_match.group(1)
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                venue=self.config.get('name', ''),
                venue_type='conference',
                url=paper_url,
                pdf_url=pdf_url,
                pages=pages,
                metadata={
                    'acl_id': paper_id,
                    'bibtex_url': bibtex_url
                }
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing ACL paper entry: {e}")
            return None
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific paper."""
        paper_url = f"{self.acl_config['base_url']}/{paper_id}.html"
        
        response = self.get_page(paper_url)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        
        # Extract abstract
        abstract_elem = soup.find('div', class_='card-body acl-abstract')
        abstract = None
        if abstract_elem:
            abstract_text = abstract_elem.find('span')
            if abstract_text:
                abstract = self.clean_text(abstract_text.text)
        
        # Extract BibTeX
        bibtex = self.get_bibtex(paper_id)
        
        return {
            'abstract': abstract,
            'bibtex': bibtex
        }
    
    def get_bibtex(self, paper_id: str) -> Optional[str]:
        """Get BibTeX citation for a paper."""
        bibtex_url = f"{self.acl_config['api_base']}/{paper_id}"
        
        response = self.get_page(bibtex_url)
        if not response:
            return None
        
        return response.text
    
    def search_papers(self, query: str, venue: Optional[str] = None) -> List[Paper]:
        """Search papers in ACL Anthology."""
        # ACL Anthology search functionality would need to be implemented
        # based on their search API or by scraping search results
        search_url = f"{self.acl_config['base_url']}/search/"
        
        params = {'q': query}
        if venue:
            params['venue'] = venue
        
        response = self.get_page(search_url, params=params)
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        return self._parse_search_results(soup)
    
    def _parse_search_results(self, soup) -> List[Paper]:
        """Parse search results from ACL Anthology."""
        papers = []
        
        # Implementation would depend on the structure of ACL search results
        # This is a placeholder for the actual implementation
        
        return papers