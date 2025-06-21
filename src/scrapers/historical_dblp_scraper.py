"""
Enhanced DBLP scraper that handles historical conference mappings and predecessor conferences.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin

from .dblp_scraper import DBLPScraper
from src.models.paper import Paper, Author, ConferenceInfo
from config.conferences import DBLP_CONFIG
from config.conference_history import get_venue_for_year, conference_exists_in_year, get_predecessor_conferences


class HistoricalDBLPScraper(DBLPScraper):
    """Enhanced DBLP scraper that handles historical conference mappings."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        super().__init__(conference_config)
        # Try to get conference name from config, fallback to venue_short
        self.conference_name = conference_config.get('conference_name', conference_config.get('venue_short', '')).upper()
        
        # Handle special case for NIPS/NeurIPS mapping
        if self.conference_name == 'NEURIPS':
            self.conference_name = 'NIPS'
        
    def scrape_papers(self, year: int, **kwargs) -> List[Paper]:
        """Scrape papers from DBLP for a specific year, handling historical mappings."""
        
        # Check if conference existed in that year
        if not conference_exists_in_year(self.conference_name, year):
            self.logger.info(f"{self.conference_name} did not exist in {year}")
            return []
        
        try:
            # Get the appropriate venue mapping for this year
            venue_key, venue_short = get_venue_for_year(self.conference_name, year)
            
            # Extract venue path from venue key (e.g., 'conf/icse' -> 'conf/icse')
            venue_path = venue_key
            
            xml_url = self.dblp_config['xml_url'].format(
                venue_path=venue_path, 
                venue_short=venue_short, 
                year=year
            )
            
            self.logger.info(f"Fetching {self.conference_name} {year} from {xml_url}")
            
            response = self.get_page(xml_url)
            if not response:
                # Try alternative approach for predecessor conferences
                return self._try_predecessor_conferences(year)
            
            papers = self._parse_dblp_xml(response.text, year)
            
            # If no papers found, try predecessor conferences
            if not papers:
                papers = self._try_predecessor_conferences(year)
            
            # Update venue name in papers to use current conference name
            for paper in papers:
                paper.venue = self.config.get('name', self.conference_name)
                paper.metadata = paper.metadata or {}
                paper.metadata.update({
                    'historical_venue_key': venue_key,
                    'historical_venue_short': venue_short,
                    'current_conference': self.conference_name
                })
            
            return papers
            
        except ValueError as e:
            self.logger.warning(f"No venue mapping for {self.conference_name} in {year}: {e}")
            return []
    
    def _try_predecessor_conferences(self, year: int) -> List[Paper]:
        """Try to fetch papers from predecessor conferences."""
        predecessors = get_predecessor_conferences(self.conference_name)
        
        all_papers = []
        for predecessor in predecessors:
            try:
                # Construct URL for predecessor
                xml_url = self.dblp_config['xml_url'].format(
                    venue_path=f'conf/{predecessor}',
                    venue_short=predecessor,
                    year=year
                )
                
                self.logger.info(f"Trying predecessor {predecessor} for {year}")
                
                response = self.get_page(xml_url)
                if response:
                    papers = self._parse_dblp_xml(response.text, year)
                    
                    # Mark papers as coming from predecessor
                    for paper in papers:
                        paper.metadata = paper.metadata or {}
                        paper.metadata.update({
                            'predecessor_conference': predecessor,
                            'current_conference': self.conference_name
                        })
                    
                    all_papers.extend(papers)
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch from predecessor {predecessor}: {e}")
        
        return all_papers
    
    def scrape_papers_range(self, start_year: int, end_year: int) -> Dict[int, List[Paper]]:
        """Scrape papers for a range of years, handling historical mappings."""
        results = {}
        
        for year in range(start_year, end_year + 1):
            self.logger.info(f"Scraping {self.conference_name} for year {year}")
            
            try:
                papers = self.scrape_papers(year)
                results[year] = papers
                
                if papers:
                    self.logger.info(f"Found {len(papers)} papers for {self.conference_name} {year}")
                else:
                    self.logger.warning(f"No papers found for {self.conference_name} {year}")
                    
            except Exception as e:
                self.logger.error(f"Error scraping {self.conference_name} {year}: {e}")
                results[year] = []
        
        return results
    
    def get_conference_timeline(self) -> Dict[str, Any]:
        """Get a timeline of conference changes and predecessors."""
        timeline = {
            'current_name': self.conference_name,
            'full_name': self.config.get('name', ''),
            'predecessors': get_predecessor_conferences(self.conference_name),
            'year_mappings': {},
            'available_years': []
        }
        
        # Get venue mappings for all years
        for year in range(2009, 2025):
            if conference_exists_in_year(self.conference_name, year):
                try:
                    venue_key, venue_short = get_venue_for_year(self.conference_name, year)
                    timeline['year_mappings'][year] = {
                        'venue_key': venue_key,
                        'venue_short': venue_short
                    }
                    timeline['available_years'].append(year)
                except ValueError:
                    pass
        
        return timeline
    
    def validate_historical_availability(self, start_year: int = 2009, end_year: int = 2024) -> Dict[int, bool]:
        """Validate which years have data available for this conference."""
        availability = {}
        
        for year in range(start_year, end_year + 1):
            if not conference_exists_in_year(self.conference_name, year):
                availability[year] = False
                continue
                
            try:
                venue_key, venue_short = get_venue_for_year(self.conference_name, year)
                venue_path = venue_key
                
                xml_url = self.dblp_config['xml_url'].format(
                    venue_path=venue_path,
                    venue_short=venue_short,
                    year=year
                )
                
                # Check if URL is accessible
                response = self.get_page(xml_url)
                availability[year] = response is not None and response.status_code == 200
                
            except Exception:
                availability[year] = False
        
        return availability