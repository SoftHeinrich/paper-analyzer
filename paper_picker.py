#!/usr/bin/env python3
"""
Paper Picker - Simple tool to list conference papers and generate search URLs
"""

import json
import argparse
import sys
from typing import List, Dict, Any
from urllib.parse import quote_plus

from src.utils.storage import StorageManager


def load_conference_papers(conference_file: str) -> List[Dict[str, Any]]:
    """Load papers from a conference JSON file."""
    try:
        storage = StorageManager()
        papers = storage.load_papers(conference_file)
        return papers
    except Exception as e:
        print(f"Error loading conference file: {e}")
        return []


def list_papers_with_numbers(papers: List[Dict[str, Any]], start: int = 1, end: int = None):
    """Display papers with numbers for easy selection."""
    if end is None:
        end = len(papers)
    
    end = min(end, len(papers))
    
    print(f"\nShowing papers {start}-{end} of {len(papers)}:")
    print("=" * 80)
    
    for i in range(start - 1, end):
        paper = papers[i]
        title = paper.get('title', 'No title')
        authors = paper.get('authors', [])
        author_names = [author.get('name', '') for author in authors]
        
        print(f"{i+1:3d}. {title}")
        if author_names:
            print(f"     Authors: {', '.join(author_names[:3])}")
            if len(author_names) > 3:
                print(f"              ... and {len(author_names) - 3} more")
        print(f"     Year: {paper.get('year', 'Unknown')}")
        if paper.get('track_type'):
            print(f"     Track: {paper.get('track_type')}")
        print()


def generate_search_urls(paper_title: str, paper_authors: List[str] = None):
    """Generate search URLs for manual citation lookup."""
    print(f"\nSearch URLs for: '{paper_title}'")
    print("=" * 80)
    
    # Clean title for URLs
    clean_title = paper_title.replace('"', '').replace("'", "")
    
    # Google Scholar URL
    scholar_query = f'"{clean_title}"'
    scholar_url = f"https://scholar.google.com/scholar?q={quote_plus(scholar_query)}&hl=en"
    print(f"Google Scholar:")
    print(f"  {scholar_url}")
    print()
    
    # Semantic Scholar URL
    semantic_query = clean_title.replace(":", "").replace("?", "")
    semantic_url = f"https://www.semanticscholar.org/search?q={quote_plus(semantic_query)}"
    print(f"Semantic Scholar:")
    print(f"  {semantic_url}")
    print()
    
    # DBLP URL (if authors provided)
    if paper_authors:
        first_author = paper_authors[0].split()[-1]  # Last name
        dblp_query = f"{first_author} {clean_title.split()[0]}"
        dblp_url = f"https://dblp.org/search?q={quote_plus(dblp_query)}"
        print(f"DBLP:")
        print(f"  {dblp_url}")
        print()
    
    # ACM Digital Library URL  
    acm_url = f"https://dl.acm.org/action/doSearch?AllField={quote_plus(clean_title)}"
    print(f"ACM Digital Library:")
    print(f"  {acm_url}")
    print()
    
    # IEEE Xplore URL
    ieee_url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={quote_plus(clean_title)}"
    print(f"IEEE Xplore:")
    print(f"  {ieee_url}")
    print()


def save_paper_info(paper: Dict[str, Any], paper_number: int):
    """Save paper information to a file for reference."""
    storage = StorageManager()
    
    title = paper.get('title', 'No title')
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')[:50]
    
    paper_info = {
        'paper_number': paper_number,
        'title': title,
        'authors': [author.get('name', '') for author in paper.get('authors', [])],
        'year': paper.get('year'),
        'venue': paper.get('venue'),
        'doi': paper.get('doi'),
        'url': paper.get('url'),
        'search_urls': {}
    }
    
    # Generate search URLs
    authors = [author.get('name', '') for author in paper.get('authors', [])]
    clean_title = title.replace('"', '').replace("'", "")
    
    scholar_query = f'"{clean_title}"'
    paper_info['search_urls'] = {
        'google_scholar': f"https://scholar.google.com/scholar?q={quote_plus(scholar_query)}&hl=en",
        'semantic_scholar': f"https://www.semanticscholar.org/search?q={quote_plus(clean_title)}",
        'acm_dl': f"https://dl.acm.org/action/doSearch?AllField={quote_plus(clean_title)}",
        'ieee_xplore': f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={quote_plus(clean_title)}"
    }
    
    if authors:
        first_author = authors[0].split()[-1]
        dblp_query = f"{first_author} {clean_title.split()[0]}"
        paper_info['search_urls']['dblp'] = f"https://dblp.org/search?q={quote_plus(dblp_query)}"
    
    # Save to file
    info_file = storage.output_dir / f"paper_{paper_number:03d}_{safe_title}_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(paper_info, f, indent=2, ensure_ascii=False)
    
    print(f"Paper info saved to: {info_file}")
    return str(info_file)


def interactive_mode(papers: List[Dict[str, Any]]):
    """Interactive mode for browsing papers."""
    current_page = 1
    papers_per_page = 10
    
    while True:
        start = (current_page - 1) * papers_per_page + 1
        end = min(current_page * papers_per_page, len(papers))
        
        list_papers_with_numbers(papers, start, end)
        
        total_pages = (len(papers) + papers_per_page - 1) // papers_per_page
        print(f"Page {current_page} of {total_pages}")
        print("\nOptions:")
        print("n - Next page")
        print("p - Previous page") 
        print("g - Go to page number")
        print("s - Select paper by number")
        print("q - Quit")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'n' and current_page < total_pages:
            current_page += 1
        elif choice == 'p' and current_page > 1:
            current_page -= 1
        elif choice == 'g':
            try:
                page_num = int(input(f"Enter page number (1-{total_pages}): "))
                if 1 <= page_num <= total_pages:
                    current_page = page_num
                else:
                    print("Invalid page number!")
            except ValueError:
                print("Please enter a valid number!")
        elif choice == 's':
            try:
                paper_num = int(input(f"Enter paper number (1-{len(papers)}): "))
                if 1 <= paper_num <= len(papers):
                    selected_paper = papers[paper_num - 1]
                    title = selected_paper['title']
                    authors = [author.get('name', '') for author in selected_paper.get('authors', [])]
                    
                    print(f"\nSelected Paper #{paper_num}:")
                    print(f"Title: {title}")
                    print(f"Authors: {', '.join(authors)}")
                    print(f"Year: {selected_paper.get('year', 'Unknown')}")
                    if selected_paper.get('track_type'):
                        print(f"Track: {selected_paper.get('track_type')}")
                    
                    # Generate search URLs
                    generate_search_urls(title, authors)
                    
                    # Ask if user wants to save paper info
                    save_choice = input("\nSave paper info to file? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        save_paper_info(selected_paper, paper_num)
                    
                    input("\nPress Enter to continue...")
                else:
                    print("Invalid paper number!")
            except ValueError:
                print("Please enter a valid number!")
        elif choice == 'q':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Paper Picker - Browse conference papers and generate search URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file output/ICSE_2014.json
  %(prog)s --file output/ICSE_2014.json --paper 5
  %(prog)s --file output/ICSE_2014.json --list --range 1 10
        """
    )
    
    parser.add_argument('--file', required=True, metavar='PATH',
                       help='Conference JSON file (e.g., output/ICSE_2014.json)')
    parser.add_argument('--paper', type=int, metavar='NUMBER',
                       help='Show details and search URLs for specific paper number')
    parser.add_argument('--list', action='store_true',
                       help='List all papers with numbers')
    parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Show papers in range (e.g., --range 1 10)')
    parser.add_argument('--save-info', action='store_true',
                       help='Save paper info to file when using --paper')
    
    args = parser.parse_args()
    
    # Load papers from conference file
    papers = load_conference_papers(args.file)
    if not papers:
        print("No papers found in the file!")
        sys.exit(1)
    
    print(f"Loaded {len(papers)} papers from {args.file}")
    
    # Handle different modes
    if args.list:
        if args.range:
            list_papers_with_numbers(papers, args.range[0], args.range[1])
        else:
            list_papers_with_numbers(papers)
            
    elif args.paper:
        if not (1 <= args.paper <= len(papers)):
            print(f"Invalid paper number! Must be between 1 and {len(papers)}")
            sys.exit(1)
            
        selected_paper = papers[args.paper - 1]
        title = selected_paper['title']
        authors = [author.get('name', '') for author in selected_paper.get('authors', [])]
        
        print(f"\nPaper #{args.paper}:")
        print(f"Title: {title}")
        print(f"Authors: {', '.join(authors)}")
        print(f"Year: {selected_paper.get('year', 'Unknown')}")
        if selected_paper.get('track_type'):
            print(f"Track: {selected_paper.get('track_type')}")
        if selected_paper.get('doi'):
            print(f"DOI: {selected_paper['doi']}")
        
        # Generate search URLs
        generate_search_urls(title, authors)
        
        # Save paper info if requested
        if args.save_info:
            save_paper_info(selected_paper, args.paper)
            
    else:
        # Interactive mode
        interactive_mode(papers)


if __name__ == '__main__':
    main()