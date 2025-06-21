"""
Citation tracking and analysis utilities.
"""

import json
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
import logging

from src.models.paper import Paper, CitationNetwork, CitationEntry
from .storage import StorageManager


class CitationAnalyzer:
    """Analyze citation patterns and networks."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_citation_network(self, network: CitationNetwork) -> Dict[str, Any]:
        """Analyze a citation network and provide insights."""
        analysis = {
            'central_paper': {
                'title': network.central_paper.title,
                'year': network.central_paper.year,
                'citation_count': network.central_paper.citation_count or 0
            },
            'network_stats': {
                'total_papers': network.get_total_papers(),
                'citations_found': len(network.citations),
                'references_found': len(network.references),
                'citation_ratio': len(network.citations) / max(1, len(network.references))
            },
            'temporal_analysis': self._analyze_temporal_patterns(network),
            'venue_analysis': self._analyze_venue_patterns(network),
            'author_analysis': self._analyze_author_patterns(network),
            'impact_metrics': self._calculate_impact_metrics(network)
        }
        
        return analysis
    
    def _analyze_temporal_patterns(self, network: CitationNetwork) -> Dict[str, Any]:
        """Analyze temporal patterns in citation network."""
        central_year = network.central_paper.year
        
        # Analyze reference years (papers cited by central paper)
        ref_years = [ref.year for ref in network.references if ref.year]
        cite_years = [cite.year for cite in network.citations if cite.year]
        
        temporal_stats = {
            'central_paper_year': central_year,
            'reference_years': {
                'count': len(ref_years),
                'range': (min(ref_years), max(ref_years)) if ref_years else None,
                'avg_age': central_year - (sum(ref_years) / len(ref_years)) if ref_years and central_year else None
            },
            'citation_years': {
                'count': len(cite_years),
                'range': (min(cite_years), max(cite_years)) if cite_years else None,
                'years_since_publication': max(cite_years) - central_year if cite_years and central_year else None
            }
        }
        
        return temporal_stats
    
    def _analyze_venue_patterns(self, network: CitationNetwork) -> Dict[str, Any]:
        """Analyze venue patterns in citation network."""
        # Count venues in references and citations
        ref_venues = Counter([ref.venue for ref in network.references if ref.venue])
        cite_venues = Counter([cite.venue for cite in network.citations if cite.venue])
        
        return {
            'central_venue': network.central_paper.venue,
            'reference_venues': dict(ref_venues.most_common(10)),
            'citation_venues': dict(cite_venues.most_common(10)),
            'venue_diversity': {
                'references': len(ref_venues),
                'citations': len(cite_venues)
            }
        }
    
    def _analyze_author_patterns(self, network: CitationNetwork) -> Dict[str, Any]:
        """Analyze author patterns in citation network."""
        central_authors = set(author.name for author in network.central_paper.authors)
        
        # Find frequent citing/referenced authors
        ref_authors = []
        for ref in network.references:
            ref_authors.extend([author.name for author in ref.authors])
        
        cite_authors = []
        for cite in network.citations:
            cite_authors.extend([author.name for author in cite.authors])
        
        ref_author_counts = Counter(ref_authors)
        cite_author_counts = Counter(cite_authors)
        
        # Find potential collaborators (authors who appear in both citations and references)
        ref_author_set = set(ref_authors)
        cite_author_set = set(cite_authors)
        potential_collaborators = ref_author_set & cite_author_set
        
        return {
            'central_authors': list(central_authors),
            'top_referenced_authors': dict(ref_author_counts.most_common(10)),
            'top_citing_authors': dict(cite_author_counts.most_common(10)),
            'potential_collaborators': list(potential_collaborators),
            'author_network_size': len(set(ref_authors + cite_authors))
        }
    
    def _calculate_impact_metrics(self, network: CitationNetwork) -> Dict[str, Any]:
        """Calculate various impact metrics."""
        citations = [cite.citation_count for cite in network.citations if cite.citation_count]
        references = [ref.citation_count for ref in network.references if ref.citation_count]
        
        metrics = {
            'direct_citations': len(network.citations),
            'references_made': len(network.references),
            'citing_papers_avg_citations': sum(citations) / len(citations) if citations else 0,
            'referenced_papers_avg_citations': sum(references) / len(references) if references else 0,
            'network_total_citations': sum(citations + references + [network.central_paper.citation_count or 0]),
            'influence_score': self._calculate_influence_score(network)
        }
        
        return metrics
    
    def _calculate_influence_score(self, network: CitationNetwork) -> float:
        """Calculate a simple influence score based on citation patterns."""
        # Simple scoring: citations + references + average impact of citing papers
        base_score = len(network.citations) + len(network.references)
        
        # Bonus for high-impact citing papers
        high_impact_bonus = sum(1 for cite in network.citations if cite.citation_count and cite.citation_count > 50)
        
        # Bonus for recent citations (more recent = higher score)
        recent_bonus = sum(1 for cite in network.citations 
                          if cite.year and cite.year >= (network.central_paper.year or 0) + 2)
        
        return base_score + high_impact_bonus * 2 + recent_bonus * 0.5


class CitationTracker:
    """Track and manage citation relationships."""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_citation_network(self, network: CitationNetwork, filename: str) -> str:
        """Save citation network to file."""
        network_data = {
            'central_paper': network.central_paper.to_dict(),
            'references': [ref.to_dict() for ref in network.references],
            'citations': [cite.to_dict() for cite in network.citations],
            'depth': network.depth,
            'total_papers': network.get_total_papers(),
            'citation_graph': network.get_citation_graph()
        }
        
        file_path = self.storage.output_dir / f"{filename}_citation_network.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def load_citation_network(self, filename: str) -> Optional[CitationNetwork]:
        """Load citation network from file."""
        file_path = self.storage.output_dir / f"{filename}_citation_network.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct Paper objects (simplified - you might want more robust deserialization)
            central_paper_data = data['central_paper']
            central_paper = Paper(
                title=central_paper_data['title'],
                authors=[],  # Simplified for brevity
                year=central_paper_data.get('year'),
                venue=central_paper_data.get('venue'),
                doi=central_paper_data.get('doi'),
                citation_count=central_paper_data.get('citation_count')
            )
            
            # Load references and citations (simplified)
            references = []
            citations = []
            
            network = CitationNetwork(
                central_paper=central_paper,
                references=references,
                citations=citations,
                depth=data.get('depth', 1)
            )
            
            return network
            
        except Exception as e:
            self.logger.error(f"Error loading citation network: {e}")
            return None
    
    def export_citation_graph(self, network: CitationNetwork, format: str = 'graphml') -> str:
        """Export citation network as graph for visualization."""
        if format == 'graphml':
            return self._export_graphml(network)
        elif format == 'dot':
            return self._export_dot(network)
        elif format == 'json':
            return self._export_json_graph(network)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_graphml(self, network: CitationNetwork) -> str:
        """Export as GraphML format for tools like Gephi."""
        central_id = network.central_paper.doi or network.central_paper.title
        
        graphml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="title" for="node" attr.name="title" attr.type="string"/>
  <key id="year" for="node" attr.name="year" attr.type="int"/>
  <key id="citations" for="node" attr.name="citations" attr.type="int"/>
  <key id="type" for="edge" attr.name="type" attr.type="string"/>
  <graph id="CitationNetwork" edgedefault="directed">
'''
        
        # Add central paper node
        graphml += f'''    <node id="{central_id}">
      <data key="title">{network.central_paper.title}</data>
      <data key="year">{network.central_paper.year or 0}</data>
      <data key="citations">{network.central_paper.citation_count or 0}</data>
    </node>
'''
        
        # Add reference nodes and edges
        for ref in network.references:
            ref_id = ref.doi or ref.title
            graphml += f'''    <node id="{ref_id}">
      <data key="title">{ref.title}</data>
      <data key="year">{ref.year or 0}</data>
      <data key="citations">{ref.citation_count or 0}</data>
    </node>
    <edge source="{central_id}" target="{ref_id}">
      <data key="type">references</data>
    </edge>
'''
        
        # Add citation nodes and edges
        for cite in network.citations:
            cite_id = cite.doi or cite.title
            graphml += f'''    <node id="{cite_id}">
      <data key="title">{cite.title}</data>
      <data key="year">{cite.year or 0}</data>
      <data key="citations">{cite.citation_count or 0}</data>
    </node>
    <edge source="{cite_id}" target="{central_id}">
      <data key="type">cites</data>
    </edge>
'''
        
        graphml += '''  </graph>
</graphml>'''
        
        # Save to file
        filename = f"citation_network_{central_id.replace('/', '_')}.graphml"
        file_path = self.storage.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(graphml)
        
        return str(file_path)
    
    def _export_json_graph(self, network: CitationNetwork) -> str:
        """Export as JSON graph format."""
        central_id = network.central_paper.doi or network.central_paper.title
        
        nodes = []
        edges = []
        
        # Add central paper
        nodes.append({
            'id': central_id,
            'title': network.central_paper.title,
            'year': network.central_paper.year,
            'citations': network.central_paper.citation_count,
            'type': 'central'
        })
        
        # Add references
        for ref in network.references:
            ref_id = ref.doi or ref.title
            nodes.append({
                'id': ref_id,
                'title': ref.title,
                'year': ref.year,
                'citations': ref.citation_count,
                'type': 'reference'
            })
            edges.append({
                'source': central_id,
                'target': ref_id,
                'type': 'references'
            })
        
        # Add citations
        for cite in network.citations:
            cite_id = cite.doi or cite.title
            nodes.append({
                'id': cite_id,
                'title': cite.title,
                'year': cite.year,
                'citations': cite.citation_count,
                'type': 'citation'
            })
            edges.append({
                'source': cite_id,
                'target': central_id,
                'type': 'cites'
            })
        
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'central_paper': network.central_paper.title,
                'total_papers': len(nodes),
                'total_edges': len(edges)
            }
        }
        
        # Save to file
        filename = f"citation_graph_{central_id.replace('/', '_')}.json"
        file_path = self.storage.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)


class CitationRecommender:
    """Recommend related papers based on citation patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def recommend_papers_to_cite(self, network: CitationNetwork, limit: int = 10) -> List[Paper]:
        """Recommend papers that should be cited based on citation network analysis."""
        recommendations = []
        
        # Find papers that are frequently cited together with references
        reference_authors = set()
        for ref in network.references:
            reference_authors.update(author.name for author in ref.authors)
        
        # Look for highly cited papers from the same authors
        author_papers = []
        for cite in network.citations:
            cite_authors = set(author.name for author in cite.authors)
            if cite_authors & reference_authors:  # Common authors
                author_papers.append(cite)
        
        # Sort by citation count and recency
        author_papers.sort(key=lambda p: (p.citation_count or 0, p.year or 0), reverse=True)
        recommendations.extend(author_papers[:limit//2])
        
        # Find papers from similar venues
        central_venue = network.central_paper.venue
        if central_venue:
            venue_papers = [cite for cite in network.citations 
                           if cite.venue and central_venue.lower() in cite.venue.lower()]
            venue_papers.sort(key=lambda p: (p.citation_count or 0, p.year or 0), reverse=True)
            recommendations.extend(venue_papers[:limit//2])
        
        # Remove duplicates and limit
        seen = set()
        unique_recommendations = []
        for paper in recommendations:
            paper_id = paper.doi or paper.title
            if paper_id not in seen:
                seen.add(paper_id)
                unique_recommendations.append(paper)
        
        return unique_recommendations[:limit]
    
    def find_potential_collaborators(self, network: CitationNetwork) -> List[Dict[str, Any]]:
        """Find potential collaborators based on citation patterns."""
        central_authors = set(author.name for author in network.central_paper.authors)
        
        # Count author appearances in citations
        author_counts = Counter()
        author_papers = defaultdict(list)
        
        for cite in network.citations:
            for author in cite.authors:
                if author.name not in central_authors:
                    author_counts[author.name] += 1
                    author_papers[author.name].append(cite)
        
        # Find authors with multiple citing papers
        collaborators = []
        for author_name, count in author_counts.most_common(20):
            if count >= 2:  # Cited multiple times
                papers = author_papers[author_name]
                collaborators.append({
                    'name': author_name,
                    'papers_count': count,
                    'recent_paper': max(papers, key=lambda p: p.year or 0),
                    'total_citations': sum(p.citation_count or 0 for p in papers),
                    'venues': list(set(p.venue for p in papers if p.venue))
                })
        
        return collaborators