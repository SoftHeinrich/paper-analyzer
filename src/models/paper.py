"""
Data models for paper information.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Author:
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None


@dataclass 
class Paper:
    title: str
    authors: List[Author]
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    venue_type: Optional[str] = None  # conference, journal, workshop
    track_type: Optional[str] = None  # oral, spotlight, poster, main, etc.
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    bibtex: Optional[str] = None
    citation_count: Optional[int] = None
    pages: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    references: List[str] = field(default_factory=list)  # DOIs/URLs of papers this cites
    cited_by: List[str] = field(default_factory=list)    # DOIs/URLs of papers citing this
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary for serialization."""
        return {
            'title': self.title,
            'authors': [
                {
                    'name': author.name,
                    'affiliation': author.affiliation,
                    'email': author.email,
                    'orcid': author.orcid
                }
                for author in self.authors
            ],
            'abstract': self.abstract,
            'keywords': self.keywords,
            'year': self.year,
            'venue': self.venue,
            'venue_type': self.venue_type,
            'track_type': self.track_type,
            'doi': self.doi,
            'url': self.url,
            'pdf_url': self.pdf_url,
            'bibtex': self.bibtex,
            'citation_count': self.citation_count,
            'pages': self.pages,
            'volume': self.volume,
            'issue': self.issue,
            'publisher': self.publisher,
            'isbn': self.isbn,
            'references': self.references,
            'cited_by': self.cited_by,
            'metadata': self.metadata,
            'scraped_at': self.scraped_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert paper to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def to_bibtex(self) -> str:
        """Generate BibTeX entry for the paper."""
        if self.bibtex:
            return self.bibtex
            
        # Generate basic BibTeX entry
        entry_type = 'inproceedings' if self.venue_type == 'conference' else 'article'
        key = self._generate_bibtex_key()
        
        bibtex = f"@{entry_type}{{{key},\n"
        bibtex += f"  title={{{self.title}}},\n"
        
        if self.authors:
            authors_str = ' and '.join([author.name for author in self.authors])
            bibtex += f"  author={{{authors_str}}},\n"
        
        if self.venue:
            venue_field = 'booktitle' if entry_type == 'inproceedings' else 'journal'
            bibtex += f"  {venue_field}={{{self.venue}}},\n"
        
        if self.year:
            bibtex += f"  year={{{self.year}}},\n"
        
        if self.pages:
            bibtex += f"  pages={{{self.pages}}},\n"
        
        if self.doi:
            bibtex += f"  doi={{{self.doi}}},\n"
        
        if self.url:
            bibtex += f"  url={{{self.url}}},\n"
        
        bibtex += "}"
        return bibtex
    
    def _generate_bibtex_key(self) -> str:
        """Generate a BibTeX key for the paper."""
        if not self.authors:
            key = "unknown"
        else:
            first_author = self.authors[0].name.split()[-1]  # Last name
            key = first_author.lower()
        
        if self.year:
            key += str(self.year)
        
        # Add first word of title for uniqueness
        if self.title:
            first_word = self.title.split()[0].lower()
            key += first_word
        
        return key


@dataclass
class CitationEntry:
    """Represents a citation relationship between papers."""
    citing_paper: str  # DOI or unique identifier
    cited_paper: str   # DOI or unique identifier
    context: Optional[str] = None  # Context where citation appears
    section: Optional[str] = None  # Paper section (intro, related work, etc.)
    citation_type: Optional[str] = None  # supportive, critical, neutral, etc.


@dataclass
class CitationNetwork:
    """Represents a citation network for analysis."""
    central_paper: Paper
    references: List[Paper] = field(default_factory=list)  # Papers cited by central paper
    citations: List[Paper] = field(default_factory=list)   # Papers citing central paper
    depth: int = 1  # How many levels deep the network goes
    
    def get_total_papers(self) -> int:
        """Get total number of papers in the network."""
        return 1 + len(self.references) + len(self.citations)
    
    def get_citation_graph(self) -> Dict[str, List[str]]:
        """Get citation relationships as adjacency list."""
        graph = {}
        
        # Central paper cites references
        central_id = self.central_paper.doi or self.central_paper.url or self.central_paper.title
        graph[central_id] = [ref.doi or ref.url or ref.title for ref in self.references]
        
        # Citations cite central paper
        for citation in self.citations:
            citation_id = citation.doi or citation.url or citation.title
            if citation_id not in graph:
                graph[citation_id] = []
            graph[citation_id].append(central_id)
        
        return graph


@dataclass
class ConferenceInfo:
    name: str
    acronym: str
    year: int
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    website: Optional[str] = None
    papers: List[Paper] = field(default_factory=list)
    
    def add_paper(self, paper: Paper):
        """Add a paper to the conference."""
        paper.venue = self.acronym
        paper.year = self.year
        self.papers.append(paper)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conference info to dictionary."""
        return {
            'name': self.name,
            'acronym': self.acronym,
            'year': self.year,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'website': self.website,
            'papers': [paper.to_dict() for paper in self.papers],
            'total_papers': len(self.papers)
        }