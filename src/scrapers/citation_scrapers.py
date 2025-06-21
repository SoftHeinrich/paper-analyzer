"""
Citation scrapers for finding references and citations of papers.
"""

import json
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote_plus
import logging

import requests
from src.models.paper import Paper, Author, CitationNetwork, CitationEntry


class SemanticScholarScraper:
    """Scraper for Semantic Scholar API to get citations and references."""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
    
    def __enter__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PaperHelper/1.0 (https://github.com/paperhelper/paperhelper)'
        })
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get a web page with error handling."""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
        
    def search_paper_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a paper by title using Semantic Scholar API."""
        search_url = f"{self.base_url}/paper/search"
        params = {
            'query': title,
            'limit': 10,
            'fields': 'paperId,title,authors,year,venue,citationCount,referenceCount,doi,url'
        }
        
        response = self.get_page(search_url, params=params)
        if not response:
            return None
        
        try:
            data = response.json()
            papers = data.get('data', [])
            
            # Find the best match
            for paper in papers:
                if self._is_title_match(title, paper.get('title', '')):
                    return paper
            
            # If no exact match, return the first result
            return papers[0] if papers else None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing Semantic Scholar response: {e}")
            return None
    
    def get_paper_citations(self, paper_id: str, limit: int = 100) -> List[Paper]:
        """Get papers that cite the given paper."""
        citations_url = f"{self.base_url}/paper/{paper_id}/citations"
        params = {
            'limit': limit,
            'fields': 'paperId,title,authors,year,venue,citationCount,doi,url,abstract'
        }
        
        response = self.get_page(citations_url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            citations = data.get('data', [])
            
            papers = []
            for citation in citations:
                citing_paper = citation.get('citingPaper', {})
                paper = self._parse_semantic_scholar_paper(citing_paper)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing citations response: {e}")
            return []
    
    def get_paper_references(self, paper_id: str, limit: int = 100) -> List[Paper]:
        """Get papers referenced by the given paper."""
        references_url = f"{self.base_url}/paper/{paper_id}/references"
        params = {
            'limit': limit,
            'fields': 'paperId,title,authors,year,venue,citationCount,doi,url,abstract'
        }
        
        response = self.get_page(references_url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            references = data.get('data', [])
            
            papers = []
            for reference in references:
                cited_paper = reference.get('citedPaper', {})
                paper = self._parse_semantic_scholar_paper(cited_paper)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing references response: {e}")
            return []
    
    def get_citation_network(self, title: str, depth: int = 1) -> Optional[CitationNetwork]:
        """Get complete citation network for a paper."""
        # First find the paper
        paper_data = self.search_paper_by_title(title)
        if not paper_data:
            self.logger.warning(f"Paper not found: {title}")
            return None
        
        # Convert to Paper object
        central_paper = self._parse_semantic_scholar_paper(paper_data)
        if not central_paper:
            return None
        
        # Get citations and references
        paper_id = paper_data.get('paperId')
        if not paper_id:
            return None
        
        citations = self.get_paper_citations(paper_id)
        references = self.get_paper_references(paper_id)
        
        return CitationNetwork(
            central_paper=central_paper,
            references=references,
            citations=citations,
            depth=depth
        )
    
    def _parse_semantic_scholar_paper(self, paper_data: Dict[str, Any]) -> Optional[Paper]:
        """Parse Semantic Scholar paper data to Paper object."""
        if not paper_data or not paper_data.get('title'):
            return None
        
        try:
            # Parse authors
            authors = []
            for author_data in paper_data.get('authors', []):
                author_name = author_data.get('name', '')
                if author_name:
                    authors.append(Author(name=author_name))
            
            # Create paper object
            paper = Paper(
                title=paper_data.get('title', ''),
                authors=authors,
                abstract=paper_data.get('abstract'),
                year=paper_data.get('year'),
                venue=paper_data.get('venue'),
                doi=paper_data.get('doi'),
                url=paper_data.get('url'),
                citation_count=paper_data.get('citationCount'),
                metadata={
                    'semantic_scholar_id': paper_data.get('paperId'),
                    'reference_count': paper_data.get('referenceCount'),
                    'source': 'semantic_scholar'
                }
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing Semantic Scholar paper: {e}")
            return None
    
    def _is_title_match(self, query_title: str, result_title: str, threshold: float = 0.8) -> bool:
        """Check if two titles match with fuzzy matching."""
        # Simple similarity based on word overlap
        query_words = set(query_title.lower().split())
        result_words = set(result_title.lower().split())
        
        if not query_words or not result_words:
            return False
        
        intersection = len(query_words & result_words)
        union = len(query_words | result_words)
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold


class CrossRefScraper:
    """Scraper for CrossRef API to get citation data."""
    
    def __init__(self):
        self.base_url = "https://api.crossref.org"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
    
    def __enter__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PaperHelper/1.0 (https://github.com/paperhelper/paperhelper)'
        })
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get a web page with error handling."""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def search_paper_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a paper by title using CrossRef API."""
        search_url = f"{self.base_url}/works"
        params = {
            'query.title': title,
            'rows': 10,
            'select': 'DOI,title,author,published-print,container-title,is-referenced-by-count,references-count,abstract'
        }
        
        response = self.get_page(search_url, params=params)
        if not response:
            return None
        
        try:
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            # Find the best match
            for item in items:
                titles = item.get('title', [])
                if titles and self._is_title_match(title, titles[0]):
                    return item
            
            # If no exact match, return the first result
            return items[0] if items else None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing CrossRef response: {e}")
            return None
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Get paper details by DOI."""
        paper_url = f"{self.base_url}/works/{doi}"
        
        response = self.get_page(paper_url)
        if not response:
            return None
        
        try:
            data = response.json()
            return data.get('message', {})
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing CrossRef paper response: {e}")
            return None
    
    def _parse_crossref_paper(self, paper_data: Dict[str, Any]) -> Optional[Paper]:
        """Parse CrossRef paper data to Paper object."""
        if not paper_data:
            return None
        
        try:
            # Parse title
            titles = paper_data.get('title', [])
            title = titles[0] if titles else ''
            
            # Parse authors
            authors = []
            for author_data in paper_data.get('author', []):
                given = author_data.get('given', '')
                family = author_data.get('family', '')
                name = f"{given} {family}".strip()
                if name:
                    authors.append(Author(
                        name=name,
                        affiliation=author_data.get('affiliation', [{}])[0].get('name') if author_data.get('affiliation') else None
                    ))
            
            # Parse publication date
            published = paper_data.get('published-print') or paper_data.get('published-online')
            year = None
            if published and 'date-parts' in published:
                date_parts = published['date-parts'][0]
                year = date_parts[0] if date_parts else None
            
            # Parse venue
            venue = None
            container_titles = paper_data.get('container-title', [])
            if container_titles:
                venue = container_titles[0]
            
            # Create paper object
            paper = Paper(
                title=title,
                authors=authors,
                abstract=paper_data.get('abstract'),
                year=year,
                venue=venue,
                doi=paper_data.get('DOI'),
                url=paper_data.get('URL'),
                citation_count=paper_data.get('is-referenced-by-count'),
                metadata={
                    'reference_count': paper_data.get('references-count'),
                    'crossref_type': paper_data.get('type'),
                    'source': 'crossref'
                }
            )
            
            return paper
            
        except Exception as e:
            self.logger.error(f"Error parsing CrossRef paper: {e}")
            return None
    
    def _is_title_match(self, query_title: str, result_title: str, threshold: float = 0.8) -> bool:
        """Check if two titles match with fuzzy matching."""
        # Simple similarity based on word overlap
        query_words = set(query_title.lower().split())
        result_words = set(result_title.lower().split())
        
        if not query_words or not result_words:
            return False
        
        intersection = len(query_words & result_words)
        union = len(query_words | result_words)
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold


class GoogleScholarScraper:
    """Enhanced scraper for Google Scholar with citation extraction."""
    
    def __init__(self):
        self.base_url = "https://scholar.google.com"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
        # User agents to rotate for better success rate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.current_ua_index = 0
    
    def __enter__(self):
        self.session = requests.Session()
        self._rotate_user_agent()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection."""
        ua = self.user_agents[self.current_ua_index % len(self.user_agents)]
        self.session.headers.update({'User-Agent': ua})
        self.current_ua_index += 1
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get a web page with error handling and anti-detection measures."""
        try:
            # Random delay between 2-5 seconds
            import random
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html_content: str):
        """Parse HTML content using BeautifulSoup."""
        from bs4 import BeautifulSoup
        return BeautifulSoup(html_content, 'html.parser')
    
    def search_paper_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a paper by title using Google Scholar."""
        search_url = f"{self.base_url}/scholar"
        params = {
            'q': f'"{title}"',  # Use quotes for exact title match
            'hl': 'en',
            'as_sdt': '0,5'  # Include patents and citations
        }
        
        response = self.get_page(search_url, params=params)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        
        # Check for captcha or blocking
        if self._is_blocked(soup):
            self.logger.warning("Google Scholar may be blocking requests")
            return None
        
        # Parse search results - try multiple selectors for robustness
        result_divs = (soup.find_all('div', class_='gs_r gs_or gs_scl') or 
                      soup.find_all('div', class_='gs_r') or
                      soup.find_all('div', attrs={'data-lid': True}))
        
        if not result_divs:
            self.logger.warning("No search results found")
            return None
        
        first_result = result_divs[0]
        result_data = self._parse_scholar_result(first_result)
        
        # Add citation URL if available
        if result_data:
            cite_link = self._extract_citation_link(first_result)
            if cite_link:
                result_data['cite_url'] = cite_link
        
        return result_data
    
    def get_citations(self, paper_title: str, max_citations: int = 50) -> List[Paper]:
        """Get papers that cite the given paper."""
        # First find the paper
        paper_data = self.search_paper_by_title(paper_title)
        if not paper_data or 'cite_url' not in paper_data:
            self.logger.warning(f"Could not find citation link for: {paper_title}")
            return []
        
        # Get citations from the citation page
        cite_url = paper_data['cite_url']
        response = self.get_page(cite_url)
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        
        # Check for blocking
        if self._is_blocked(soup):
            self.logger.warning("Google Scholar blocking citation requests")
            return []
        
        citations = []
        result_divs = (soup.find_all('div', class_='gs_r gs_or gs_scl') or 
                      soup.find_all('div', class_='gs_r'))
        
        for div in result_divs[:max_citations]:
            citation_data = self._parse_scholar_result(div)
            if citation_data:
                paper = self._convert_to_paper(citation_data)
                if paper:
                    citations.append(paper)
        
        self.logger.info(f"Found {len(citations)} citations from Google Scholar")
        return citations
    
    def get_related_papers(self, paper_title: str, max_papers: int = 20) -> List[Paper]:
        """Get related papers using Google Scholar's 'Related articles' feature."""
        # Search for the paper first
        paper_data = self.search_paper_by_title(paper_title)
        if not paper_data:
            return []
        
        # Look for related articles link
        search_url = f"{self.base_url}/scholar"
        params = {
            'q': f'"{paper_title}"',
            'hl': 'en'
        }
        
        response = self.get_page(search_url, params=params)
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        
        # Find "Related articles" link
        related_link = soup.find('a', string=re.compile(r'Related articles'))
        if not related_link:
            return []
        
        related_url = related_link.get('href')
        if related_url and related_url.startswith('/scholar'):
            related_url = f"{self.base_url}{related_url}"
            
            response = self.get_page(related_url)
            if response:
                soup = self.parse_html(response.text)
                result_divs = soup.find_all('div', class_='gs_r')[:max_papers]
                
                related_papers = []
                for div in result_divs:
                    paper_data = self._parse_scholar_result(div)
                    if paper_data:
                        paper = self._convert_to_paper(paper_data)
                        if paper:
                            related_papers.append(paper)
                
                return related_papers
        
        return []
    
    def _is_blocked(self, soup) -> bool:
        """Check if Google Scholar is blocking requests."""
        # Check for common blocking indicators
        captcha_indicators = [
            'captcha', 'robot', 'automated queries', 'unusual traffic',
            'verify you are human', 'security check'
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in captcha_indicators)
    
    def _extract_citation_link(self, result_div) -> Optional[str]:
        """Extract citation link from a search result."""
        # Look for "Cited by X" link
        cite_links = result_div.find_all('a', string=re.compile(r'Cited by \d+'))
        if cite_links:
            href = cite_links[0].get('href')
            if href and href.startswith('/scholar'):
                return f"{self.base_url}{href}"
        return None
    
    def _parse_scholar_result(self, result_div) -> Optional[Dict[str, Any]]:
        """Enhanced parsing of Google Scholar search result."""
        try:
            # Extract title - try multiple selectors
            title_element = (result_div.find('h3', class_='gs_rt') or 
                           result_div.find('h3') or
                           result_div.find('a', class_='gs_rt'))
            
            if not title_element:
                return None
            
            # Clean title text
            title = title_element.get_text(strip=True)
            # Remove [PDF] and other prefixes
            title = re.sub(r'^\[PDF\]\s*', '', title)
            title = re.sub(r'^\[HTML\]\s*', '', title)
            
            # Extract URL
            url = None
            title_link = title_element.find('a')
            if title_link and title_link.get('href'):
                url = title_link['href']
                # Convert relative URLs to absolute
                if url.startswith('/'):
                    url = f"https://scholar.google.com{url}"
            
            # Extract authors and venue info
            authors_venue = result_div.find('div', class_='gs_a')
            authors_text = ''
            venue_text = ''
            year = None
            
            if authors_venue:
                full_text = authors_venue.get_text(strip=True)
                authors_text = full_text
                
                # Try to extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', full_text)
                if year_match:
                    year = int(year_match.group())
                
                # Try to separate authors from venue
                parts = full_text.split(' - ')
                if len(parts) >= 2:
                    authors_text = parts[0]
                    venue_text = parts[1]
            
            # Extract abstract/snippet
            snippet_element = (result_div.find('span', class_='gs_rs') or
                             result_div.find('div', class_='gs_rs'))
            snippet = snippet_element.get_text(strip=True) if snippet_element else ''
            
            # Extract citation count
            citation_count = None
            cite_element = result_div.find('a', string=re.compile(r'Cited by \d+'))
            if cite_element:
                match = re.search(r'Cited by (\d+)', cite_element.text)
                if match:
                    citation_count = int(match.group(1))
            
            # Parse authors from authors_text
            authors = self._parse_authors(authors_text)
            
            return {
                'title': title,
                'authors': authors,
                'authors_venue': authors_text,
                'venue': venue_text,
                'year': year,
                'abstract': snippet,
                'url': url,
                'citation_count': citation_count,
                'source': 'google_scholar'
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Google Scholar result: {e}")
            return None
    
    def _parse_authors(self, authors_text: str) -> List[Author]:
        """Parse authors from Google Scholar author text."""
        if not authors_text:
            return []
        
        # Clean up the text - remove venue info after dash
        if ' - ' in authors_text:
            authors_text = authors_text.split(' - ')[0]
        
        # Split by common separators
        author_names = []
        if ',' in authors_text:
            # Split by commas, but be careful of "Last, First" format
            parts = authors_text.split(',')
            current_author = ""
            
            for part in parts:
                part = part.strip()
                if current_author and not part[0].isupper():
                    # This might be a first name
                    current_author += f", {part}"
                else:
                    if current_author:
                        author_names.append(current_author.strip())
                    current_author = part
            
            if current_author:
                author_names.append(current_author.strip())
        else:
            # Try other separators
            for sep in [';', ' and ', '&']:
                if sep in authors_text:
                    author_names = [name.strip() for name in authors_text.split(sep)]
                    break
            else:
                # Single author or can't parse
                author_names = [authors_text.strip()]
        
        # Convert to Author objects
        authors = []
        for name in author_names:
            if name and len(name) > 1:  # Filter out very short names
                authors.append(Author(name=name))
        
        return authors
    
    def _convert_to_paper(self, scholar_data: Dict[str, Any]) -> Optional[Paper]:
        """Convert Google Scholar data to Paper object."""
        if not scholar_data.get('title'):
            return None
        
        return Paper(
            title=scholar_data['title'],
            authors=scholar_data.get('authors', []),
            abstract=scholar_data.get('abstract'),
            year=scholar_data.get('year'),
            venue=scholar_data.get('venue'),
            url=scholar_data.get('url'),
            citation_count=scholar_data.get('citation_count'),
            metadata={
                'source': 'google_scholar',
                'authors_venue_text': scholar_data.get('authors_venue', '')
            }
        )


class CitationAggregator:
    """Aggregates citation data from multiple sources."""
    
    def __init__(self):
        self.semantic_scholar = SemanticScholarScraper()
        self.crossref = CrossRefScraper()
        self.google_scholar = GoogleScholarScraper()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def find_paper_citations(self, title: str, max_citations: int = 50, use_google_scholar: bool = True) -> Tuple[Optional[Paper], List[Paper], List[Paper]]:
        """Find citations and references for a paper from multiple sources."""
        central_paper = None
        all_citations = []
        all_references = []
        
        # Try Semantic Scholar first (most reliable API)
        try:
            with self.semantic_scholar:
                network = self.semantic_scholar.get_citation_network(title)
                if network:
                    central_paper = network.central_paper
                    all_citations.extend(network.citations[:max_citations])
                    all_references.extend(network.references[:max_citations])
                    self.logger.info(f"Found {len(network.citations)} citations and {len(network.references)} references from Semantic Scholar")
        except Exception as e:
            self.logger.error(f"Error with Semantic Scholar: {e}")
        
        # If we don't have enough data, try CrossRef
        if len(all_citations) < max_citations // 2:
            try:
                with self.crossref:
                    paper_data = self.crossref.search_paper_by_title(title)
                    if paper_data and not central_paper:
                        central_paper = self.crossref._parse_crossref_paper(paper_data)
                        self.logger.info("Found paper details from CrossRef")
            except Exception as e:
                self.logger.error(f"Error with CrossRef: {e}")
        
        # Try Google Scholar for citations if other sources failed or didn't provide enough
        if use_google_scholar and len(all_citations) < max_citations // 3:
            try:
                with self.google_scholar:
                    # First try to find the paper
                    scholar_paper_data = self.google_scholar.search_paper_by_title(title)
                    if scholar_paper_data and not central_paper:
                        central_paper = self.google_scholar._convert_to_paper(scholar_paper_data)
                        self.logger.info("Found paper details from Google Scholar")
                    
                    # Get citations from Google Scholar
                    scholar_citations = self.google_scholar.get_citations(title, max_citations)
                    if scholar_citations:
                        all_citations.extend(scholar_citations)
                        self.logger.info(f"Found {len(scholar_citations)} additional citations from Google Scholar")
                    
                    # Get related papers as potential references
                    related_papers = self.google_scholar.get_related_papers(title, max_citations // 2)
                    if related_papers:
                        all_references.extend(related_papers)
                        self.logger.info(f"Found {len(related_papers)} related papers from Google Scholar")
                        
            except Exception as e:
                self.logger.error(f"Error with Google Scholar: {e}")
        
        # Add delay to be respectful to APIs
        time.sleep(1)
        
        return central_paper, all_citations, all_references
    
    def get_enriched_citation_network(self, title: str, max_papers: int = 100) -> Optional[CitationNetwork]:
        """Get enriched citation network from multiple sources."""
        central_paper, citations, references = self.find_paper_citations(title, max_papers)
        
        if not central_paper:
            self.logger.warning(f"Could not find paper: {title}")
            return None
        
        return CitationNetwork(
            central_paper=central_paper,
            citations=citations,
            references=references,
            depth=1
        )