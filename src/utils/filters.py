"""
Filtering and search utilities for scraped papers.
"""

import re
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from src.models.paper import Paper


class PaperFilter:
    """Filter papers based on various criteria."""
    
    @staticmethod
    def by_year(papers: List[Paper], year: int) -> List[Paper]:
        """Filter papers by specific year."""
        return [paper for paper in papers if paper.year == year]
    
    @staticmethod
    def by_year_range(papers: List[Paper], start_year: int, end_year: int) -> List[Paper]:
        """Filter papers by year range (inclusive)."""
        return [
            paper for paper in papers 
            if paper.year and start_year <= paper.year <= end_year
        ]
    
    @staticmethod
    def by_venue(papers: List[Paper], venue: str, case_sensitive: bool = False) -> List[Paper]:
        """Filter papers by venue."""
        if case_sensitive:
            return [paper for paper in papers if paper.venue == venue]
        else:
            venue_lower = venue.lower()
            return [
                paper for paper in papers 
                if paper.venue and venue_lower in paper.venue.lower()
            ]
    
    @staticmethod
    def by_author(papers: List[Paper], author_name: str, case_sensitive: bool = False) -> List[Paper]:
        """Filter papers by author name."""
        matching_papers = []
        
        for paper in papers:
            for author in paper.authors:
                if case_sensitive:
                    if author_name in author.name:
                        matching_papers.append(paper)
                        break
                else:
                    if author_name.lower() in author.name.lower():
                        matching_papers.append(paper)
                        break
        
        return matching_papers
    
    @staticmethod
    def by_keyword(papers: List[Paper], keyword: str, case_sensitive: bool = False) -> List[Paper]:
        """Filter papers by keyword in title, abstract, or keywords."""
        matching_papers = []
        
        for paper in papers:
            # Check title
            if paper.title:
                text = paper.title if case_sensitive else paper.title.lower()
                search_term = keyword if case_sensitive else keyword.lower()
                if search_term in text:
                    matching_papers.append(paper)
                    continue
            
            # Check abstract
            if paper.abstract:
                text = paper.abstract if case_sensitive else paper.abstract.lower()
                search_term = keyword if case_sensitive else keyword.lower()
                if search_term in text:
                    matching_papers.append(paper)
                    continue
            
            # Check keywords
            for kw in paper.keywords:
                text = kw if case_sensitive else kw.lower()
                search_term = keyword if case_sensitive else keyword.lower()
                if search_term in text:
                    matching_papers.append(paper)
                    break
        
        return matching_papers
    
    @staticmethod
    def by_citation_count(papers: List[Paper], min_citations: int) -> List[Paper]:
        """Filter papers by minimum citation count."""
        return [
            paper for paper in papers 
            if paper.citation_count and paper.citation_count >= min_citations
        ]
    
    @staticmethod
    def has_pdf(papers: List[Paper]) -> List[Paper]:
        """Filter papers that have PDF URLs."""
        return [paper for paper in papers if paper.pdf_url]
    
    @staticmethod
    def has_doi(papers: List[Paper]) -> List[Paper]:
        """Filter papers that have DOI."""
        return [paper for paper in papers if paper.doi]
    
    @staticmethod
    def by_regex(papers: List[Paper], pattern: str, fields: List[str] = None) -> List[Paper]:
        """Filter papers using regex pattern."""
        if fields is None:
            fields = ['title', 'abstract']
        
        regex = re.compile(pattern, re.IGNORECASE)
        matching_papers = []
        
        for paper in papers:
            for field in fields:
                value = getattr(paper, field, None)
                if value and regex.search(str(value)):
                    matching_papers.append(paper)
                    break
        
        return matching_papers


class PaperSearcher:
    """Advanced search functionality for papers."""
    
    def __init__(self, papers: List[Paper]):
        self.papers = papers
    
    def search(self, query: str, fields: List[str] = None) -> List[Paper]:
        """Perform full-text search across specified fields."""
        if fields is None:
            fields = ['title', 'abstract', 'keywords']
        
        query_terms = query.lower().split()
        matching_papers = []
        
        for paper in self.papers:
            score = self._calculate_relevance_score(paper, query_terms, fields)
            if score > 0:
                matching_papers.append((paper, score))
        
        # Sort by relevance score
        matching_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, score in matching_papers]
    
    def _calculate_relevance_score(self, paper: Paper, query_terms: List[str], fields: List[str]) -> float:
        """Calculate relevance score for a paper given query terms."""
        score = 0.0
        
        for field in fields:
            value = getattr(paper, field, None)
            if not value:
                continue
            
            if isinstance(value, list):
                text = ' '.join(str(item) for item in value).lower()
            else:
                text = str(value).lower()
            
            # Calculate term frequency
            for term in query_terms:
                term_count = text.count(term)
                if term_count > 0:
                    # Weight different fields differently
                    weight = self._get_field_weight(field)
                    score += term_count * weight
        
        return score
    
    def _get_field_weight(self, field: str) -> float:
        """Get weight for different fields in relevance scoring."""
        weights = {
            'title': 3.0,
            'keywords': 2.0,
            'abstract': 1.0,
            'authors': 0.5
        }
        return weights.get(field, 1.0)
    
    def search_similar(self, reference_paper: Paper, similarity_threshold: float = 0.3) -> List[Paper]:
        """Find papers similar to a reference paper."""
        if not reference_paper.abstract:
            return []
        
        reference_words = set(reference_paper.abstract.lower().split())
        similar_papers = []
        
        for paper in self.papers:
            if paper == reference_paper or not paper.abstract:
                continue
            
            paper_words = set(paper.abstract.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(reference_words & paper_words)
            union = len(reference_words | paper_words)
            
            if union > 0:
                similarity = intersection / union
                if similarity >= similarity_threshold:
                    similar_papers.append((paper, similarity))
        
        # Sort by similarity
        similar_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, similarity in similar_papers]


class PaperAnalyzer:
    """Analyze trends and patterns in paper collections."""
    
    def __init__(self, papers: List[Paper]):
        self.papers = papers
    
    def get_yearly_distribution(self) -> Dict[int, int]:
        """Get distribution of papers by year."""
        distribution = {}
        for paper in self.papers:
            if paper.year:
                distribution[paper.year] = distribution.get(paper.year, 0) + 1
        return dict(sorted(distribution.items()))
    
    def get_venue_distribution(self) -> Dict[str, int]:
        """Get distribution of papers by venue."""
        distribution = {}
        for paper in self.papers:
            if paper.venue:
                distribution[paper.venue] = distribution.get(paper.venue, 0) + 1
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def get_top_authors(self, limit: int = 10) -> List[tuple]:
        """Get top authors by number of papers."""
        author_counts = {}
        
        for paper in self.papers:
            for author in paper.authors:
                author_counts[author.name] = author_counts.get(author.name, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        return top_authors[:limit]
    
    def get_common_keywords(self, limit: int = 20) -> List[tuple]:
        """Get most common keywords."""
        keyword_counts = {}
        
        for paper in self.papers:
            for keyword in paper.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        common_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return common_keywords[:limit]
    
    def get_citation_stats(self) -> Dict[str, Any]:
        """Get citation statistics."""
        citations = [paper.citation_count for paper in self.papers if paper.citation_count is not None]
        
        if not citations:
            return {}
        
        return {
            'total_papers_with_citations': len(citations),
            'total_citations': sum(citations),
            'average_citations': sum(citations) / len(citations),
            'median_citations': sorted(citations)[len(citations) // 2],
            'max_citations': max(citations),
            'min_citations': min(citations)
        }