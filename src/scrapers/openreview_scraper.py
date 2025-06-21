"""
OpenReview scraper for conferences like ICLR.
"""

import json
from typing import List, Dict, Any, Optional

from .base import BaseScraper
from src.models.paper import Paper, Author, ConferenceInfo
from config.conferences import OPENREVIEW_CONFIG


class OpenReviewScraper(BaseScraper):
    """Scraper for OpenReview platform."""
    
    def __init__(self, conference_config: Dict[str, Any]):
        super().__init__(conference_config)
        self.openreview_config = OPENREVIEW_CONFIG
        
    def scrape_papers(self, year: int, **kwargs) -> List[Paper]:
        """Scrape papers from OpenReview for a specific year."""
        venue_key = self.config['venue_key']
        
        # OpenReview API endpoint for getting notes
        api_url = f"{self.openreview_config['base_url']}{self.openreview_config['notes_endpoint']}"
        
        params = {
            'invitation': f"{venue_key}.cc/{year}/Conference/-/Blind_Submission",
            'details': 'replyCount,invitation,tags',
            'offset': 0,
            'limit': 1000
        }
        
        papers = []
        offset = 0
        
        while True:
            params['offset'] = offset
            response = self.get_page(api_url, params=params)
            
            if not response:
                break
            
            try:
                data = response.json()
                notes = data.get('notes', [])
                
                if not notes:
                    break
                
                for note in notes:
                    paper = self._parse_openreview_note(note, year)
                    if paper:
                        papers.append(paper)
                
                offset += len(notes)
                
                # Break if we got fewer than expected (likely the last batch)
                if len(notes) < params['limit']:
                    break
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing OpenReview JSON: {e}")
                break
        
        return papers
    
    def scrape_conference_info(self, year: int) -> ConferenceInfo:
        """Scrape conference information from OpenReview."""
        papers = self.scrape_papers(year)
        
        conference_info = ConferenceInfo(
            name=self.config['name'],
            acronym=self.config.get('venue_key', ''),
            year=year,
            papers=papers
        )
        
        return conference_info
    
    def _parse_openreview_note(self, note: Dict[str, Any], year: int) -> Optional[Paper]:
        """Parse a single note from OpenReview API."""
        try:
            content = note.get('content', {})
            
            title = content.get('title', '')
            if isinstance(title, dict):
                title = title.get('value', '')
            title = self.clean_text(str(title))
            
            if not title:
                return None
            
            # Extract authors
            authors = []
            author_data = content.get('authors', [])
            if isinstance(author_data, dict):
                author_data = author_data.get('value', [])
            
            if isinstance(author_data, list):
                for author_name in author_data:
                    if isinstance(author_name, str) and author_name.strip():
                        authors.append(Author(name=self.clean_text(author_name)))
            
            # Extract abstract
            abstract = content.get('abstract', '')
            if isinstance(abstract, dict):
                abstract = abstract.get('value', '')
            abstract = self.clean_text(str(abstract)) if abstract else None
            
            # Extract keywords
            keywords = []
            keyword_data = content.get('keywords', [])
            if isinstance(keyword_data, dict):
                keyword_data = keyword_data.get('value', [])
            if isinstance(keyword_data, list):
                keywords = [self.clean_text(str(kw)) for kw in keyword_data if kw]
            
            # Generate URLs
            note_id = note.get('id', '')
            url = f"https://openreview.net/forum?id={note_id}" if note_id else None
            pdf_url = f"https://openreview.net/pdf?id={note_id}" if note_id else None
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                keywords=keywords,
                year=year,
                venue=self.config.get('name', ''),
                venue_type='conference',
                url=url,
                pdf_url=pdf_url,
                metadata={
                    'openreview_id': note_id,
                    'invitation': note.get('invitation', ''),
                    'forum': note.get('forum', ''),
                    'reply_count': note.get('details', {}).get('replyCount', 0)
                }
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing OpenReview note: {e}")
            return None
    
    def get_paper_reviews(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get reviews for a specific paper."""
        api_url = f"{self.openreview_config['base_url']}{self.openreview_config['notes_endpoint']}"
        
        params = {
            'forum': paper_id,
            'details': 'replyCount,invitation,tags'
        }
        
        response = self.get_page(api_url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            notes = data.get('notes', [])
            
            reviews = []
            for note in notes:
                if 'Review' in note.get('invitation', ''):
                    review_content = note.get('content', {})
                    reviews.append({
                        'id': note.get('id'),
                        'rating': review_content.get('rating', {}).get('value'),
                        'confidence': review_content.get('confidence', {}).get('value'),
                        'summary': review_content.get('summary', {}).get('value', ''),
                        'strengths': review_content.get('strengths', {}).get('value', ''),
                        'weaknesses': review_content.get('weaknesses', {}).get('value', ''),
                        'questions': review_content.get('questions', {}).get('value', '')
                    })
            
            return reviews
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing reviews JSON: {e}")
            return []