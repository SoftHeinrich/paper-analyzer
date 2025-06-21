#!/usr/bin/env python3
"""
PaperHelper Web UI - A local web interface for browsing conference papers.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus
import math

app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path("output")
PAPERS_PER_PAGE = 20

def load_conference_files():
    """Load all available conference JSON files."""
    conferences = []
    if OUTPUT_DIR.exists():
        for file_path in OUTPUT_DIR.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    if 'papers' in data and data['papers']:
                        conferences.append({
                            'filename': file_path.name,
                            'name': file_path.stem,
                            'total_papers': data.get('total_papers', len(data['papers'])),
                            'scraped_at': data.get('scraped_at', 'Unknown')
                        })
            except (json.JSONDecodeError, KeyError):
                continue
    
    return sorted(conferences, key=lambda x: x['name'])

def load_papers(filename: str) -> Dict[str, Any]:
    """Load papers from a specific conference file."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return {'papers': [], 'total_papers': 0}
    
    try:
        with open(file_path) as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, KeyError):
        return {'papers': [], 'total_papers': 0}

def search_papers(papers: List[Dict], query: str) -> List[Dict]:
    """Search papers by title, authors, or keywords."""
    if not query:
        return papers
    
    query_lower = query.lower()
    results = []
    
    for paper in papers:
        # Search in title
        if query_lower in paper.get('title', '').lower():
            results.append(paper)
            continue
            
        # Search in authors
        authors = paper.get('authors', [])
        author_match = any(query_lower in author.get('name', '').lower() for author in authors)
        if author_match:
            results.append(paper)
            continue
            
        # Search in abstract
        abstract = paper.get('abstract', '')
        if abstract and query_lower in abstract.lower():
            results.append(paper)
            continue
            
        # Search in keywords
        keywords = paper.get('keywords', [])
        keyword_match = any(query_lower in keyword.lower() for keyword in keywords)
        if keyword_match:
            results.append(paper)
    
    return results

def filter_papers(papers: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Filter papers by various criteria."""
    filtered = papers
    
    # Filter by year
    if filters.get('year'):
        year = int(filters['year'])
        filtered = [p for p in filtered if p.get('year') == year]
    
    # Filter by track type
    if filters.get('track_type'):
        track = filters['track_type']
        filtered = [p for p in filtered if p.get('track_type') == track]
    
    # Filter by author count
    if filters.get('min_authors'):
        min_authors = int(filters['min_authors'])
        filtered = [p for p in filtered if len(p.get('authors', [])) >= min_authors]
    
    return filtered

def generate_search_urls(title: str, authors: List[str] = None):
    """Generate search URLs for citation lookup."""
    clean_title = title.replace('"', '').replace("'", "")
    
    urls = {
        'google_scholar': f"https://scholar.google.com/scholar?q={quote_plus(f'"{clean_title}"')}&hl=en",
        'semantic_scholar': f"https://www.semanticscholar.org/search?q={quote_plus(clean_title)}",
        'acm_dl': f"https://dl.acm.org/action/doSearch?AllField={quote_plus(clean_title)}",
        'ieee_xplore': f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={quote_plus(clean_title)}"
    }
    
    if authors:
        first_author = authors[0].split()[-1]  # Last name
        dblp_query = f"{first_author} {clean_title.split()[0]}"
        urls['dblp'] = f"https://dblp.org/search?q={quote_plus(dblp_query)}"
    
    return urls

@app.route('/')
def index():
    """Main page showing available conferences."""
    conferences = load_conference_files()
    return render_template('index.html', conferences=conferences)

@app.route('/conference/<filename>')
def conference_papers(filename):
    """Show papers for a specific conference."""
    data = load_papers(filename)
    papers = data.get('papers', [])
    
    # Get filter parameters
    search_query = request.args.get('search', '')
    year_filter = request.args.get('year', '')
    track_filter = request.args.get('track_type', '')
    page = int(request.args.get('page', 1))
    
    # Apply search and filters
    if search_query:
        papers = search_papers(papers, search_query)
    
    filters = {}
    if year_filter:
        filters['year'] = year_filter
    if track_filter:
        filters['track_type'] = track_filter
    
    if filters:
        papers = filter_papers(papers, filters)
    
    # Pagination
    total_papers = len(papers)
    total_pages = math.ceil(total_papers / PAPERS_PER_PAGE)
    start_idx = (page - 1) * PAPERS_PER_PAGE
    end_idx = start_idx + PAPERS_PER_PAGE
    page_papers = papers[start_idx:end_idx]
    
    # Get available years and track types for filters
    all_papers = data.get('papers', [])
    years = sorted(set(p.get('year') for p in all_papers if p.get('year')))
    track_types = sorted(set(p.get('track_type') for p in all_papers if p.get('track_type')))
    
    return render_template('conference.html', 
                         filename=filename,
                         conference_name=filename.replace('.json', '').replace('_', ' '),
                         papers=page_papers,
                         total_papers=total_papers,
                         total_pages=total_pages,
                         current_page=page,
                         search_query=search_query,
                         year_filter=year_filter,
                         track_filter=track_filter,
                         years=years,
                         track_types=track_types)

@app.route('/paper/<filename>/<int:paper_index>')
def paper_detail(filename, paper_index):
    """Show detailed view of a specific paper."""
    data = load_papers(filename)
    papers = data.get('papers', [])
    
    if 0 <= paper_index < len(papers):
        paper = papers[paper_index]
        authors = [author.get('name', '') for author in paper.get('authors', [])]
        search_urls = generate_search_urls(paper.get('title', ''), authors)
        
        return render_template('paper_detail.html',
                             paper=paper,
                             paper_index=paper_index,
                             filename=filename,
                             search_urls=search_urls,
                             conference_name=filename.replace('.json', '').replace('_', ' '))
    else:
        return "Paper not found", 404

@app.route('/api/conferences')
def api_conferences():
    """API endpoint for conference list."""
    return jsonify(load_conference_files())

@app.route('/api/conference/<filename>')
def api_conference_papers(filename):
    """API endpoint for conference papers."""
    data = load_papers(filename)
    return jsonify(data)

@app.route('/api/search/<filename>')
def api_search(filename):
    """API endpoint for searching papers."""
    data = load_papers(filename)
    papers = data.get('papers', [])
    
    query = request.args.get('q', '')
    year = request.args.get('year', '')
    track_type = request.args.get('track_type', '')
    
    if query:
        papers = search_papers(papers, query)
    
    filters = {}
    if year:
        filters['year'] = year
    if track_type:
        filters['track_type'] = track_type
    
    if filters:
        papers = filter_papers(papers, filters)
    
    return jsonify({
        'papers': papers,
        'total': len(papers)
    })

@app.route('/stats')
def statistics():
    """Show statistics across all conferences."""
    conferences = load_conference_files()
    stats = {
        'total_conferences': len(conferences),
        'total_papers': sum(c['total_papers'] for c in conferences),
        'conferences_by_year': {},
        'papers_by_track': {},
        'top_authors': {}
    }
    
    # Analyze all papers for detailed stats
    all_papers = []
    for conf in conferences:
        data = load_papers(conf['filename'])
        papers = data.get('papers', [])
        all_papers.extend(papers)
    
    # Count papers by year
    for paper in all_papers:
        year = paper.get('year')
        if year:
            stats['conferences_by_year'][year] = stats['conferences_by_year'].get(year, 0) + 1
    
    # Count papers by track type
    for paper in all_papers:
        track = paper.get('track_type', 'unknown')
        stats['papers_by_track'][track] = stats['papers_by_track'].get(track, 0) + 1
    
    # Count top authors
    author_counts = {}
    for paper in all_papers:
        for author in paper.get('authors', []):
            name = author.get('name', '')
            if name:
                author_counts[name] = author_counts.get(name, 0) + 1
    
    stats['top_authors'] = dict(sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)