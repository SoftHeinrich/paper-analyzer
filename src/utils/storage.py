"""
Storage utilities for saving scraped papers in different formats.
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.paper import Paper, ConferenceInfo


class StorageManager:
    """Manages storage of scraped paper data in various formats."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_papers(self, papers: List[Paper], filename: str, format: str = 'json'):
        """Save papers to file in specified format."""
        file_path = self.output_dir / f"{filename}.{format}"
        
        if format == 'json':
            self._save_json(papers, file_path)
        elif format == 'csv':
            self._save_csv(papers, file_path)
        elif format == 'bibtex':
            self._save_bibtex(papers, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return file_path
    
    def save_conference(self, conference: ConferenceInfo, format: str = 'json'):
        """Save complete conference information."""
        filename = f"{conference.acronym}_{conference.year}"
        
        if format == 'json':
            file_path = self.output_dir / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conference.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Also save papers in the specified format
        if conference.papers:
            self.save_papers(conference.papers, filename, format)
        
        return file_path
    
    def _save_json(self, papers: List[Paper], file_path: Path):
        """Save papers as JSON."""
        data = {
            'scraped_at': datetime.now().isoformat(),
            'total_papers': len(papers),
            'papers': [paper.to_dict() for paper in papers]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, papers: List[Paper], file_path: Path):
        """Save papers as CSV."""
        if not papers:
            return
        
        fieldnames = [
            'title', 'authors', 'year', 'venue', 'venue_type', 'track_type',
            'abstract', 'keywords', 'doi', 'url', 'pdf_url',
            'pages', 'citation_count', 'references', 'cited_by', 'scraped_at'
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for paper in papers:
                row = {
                    'title': paper.title or '',
                    'authors': '; '.join([author.name for author in paper.authors]) if paper.authors else '',
                    'year': paper.year or '',
                    'venue': paper.venue or '',
                    'venue_type': paper.venue_type or '',
                    'track_type': paper.track_type or '',
                    'abstract': (paper.abstract or '').replace('\n', ' ').replace('\r', ' '),
                    'keywords': '; '.join(paper.keywords) if paper.keywords else '',
                    'doi': paper.doi or '',
                    'url': paper.url or '',
                    'pdf_url': paper.pdf_url or '',
                    'pages': paper.pages or '',
                    'citation_count': paper.citation_count or '',
                    'references': '; '.join(paper.references) if paper.references else '',
                    'cited_by': '; '.join(paper.cited_by) if paper.cited_by else '',
                    'scraped_at': paper.scraped_at.isoformat()
                }
                writer.writerow(row)
    
    def _save_bibtex(self, papers: List[Paper], file_path: Path):
        """Save papers as BibTeX."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"% BibTeX entries generated on {datetime.now().isoformat()}\n")
            f.write(f"% Total papers: {len(papers)}\n\n")
            
            for paper in papers:
                f.write(paper.to_bibtex())
                f.write("\n\n")
    
    def load_papers(self, file_path: str) -> List[Dict[str, Any]]:
        """Load papers from JSON file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both formats: {"papers": [...]} and [...]
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('papers', [])
        else:
            raise ValueError(f"Invalid JSON format: expected list or dict with 'papers' key")
    
    def get_saved_files(self) -> List[Path]:
        """Get list of all saved files."""
        return list(self.output_dir.glob('*'))
    
    def cleanup_old_files(self, days: int = 30):
        """Remove files older than specified days."""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file_path in self.output_dir.iterdir():
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()


class DataExporter:
    """Export scraped data to various external formats and services."""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager
    
    def export_to_mendeley(self, papers: List[Paper]) -> str:
        """Export papers in Mendeley-compatible format."""
        # Mendeley accepts BibTeX format
        filename = f"mendeley_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return str(self.storage.save_papers(papers, filename, 'bibtex'))
    
    def export_to_zotero(self, papers: List[Paper]) -> str:
        """Export papers in Zotero-compatible format."""
        # Zotero accepts BibTeX format
        filename = f"zotero_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return str(self.storage.save_papers(papers, filename, 'bibtex'))
    
    def export_to_excel(self, papers: List[Paper]) -> str:
        """Export papers to Excel format."""
        try:
            import pandas as pd
            
            # Convert papers to DataFrame
            data = []
            for paper in papers:
                data.append({
                    'Title': paper.title,
                    'Authors': '; '.join([author.name for author in paper.authors]),
                    'Year': paper.year,
                    'Venue': paper.venue,
                    'Abstract': paper.abstract,
                    'Keywords': '; '.join(paper.keywords) if paper.keywords else '',
                    'DOI': paper.doi,
                    'URL': paper.url,
                    'PDF URL': paper.pdf_url,
                    'Pages': paper.pages,
                    'Citation Count': paper.citation_count
                })
            
            df = pd.DataFrame(data)
            filename = f"papers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = self.storage.output_dir / filename
            
            df.to_excel(file_path, index=False)
            return str(file_path)
            
        except ImportError:
            # Fallback to CSV if pandas is not available
            filename = f"papers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return str(self.storage.save_papers(papers, filename, 'csv'))