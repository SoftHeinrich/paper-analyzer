#!/usr/bin/env python3
"""
Simple Citation Finder - Streamlined tool for manual citation lookup
"""

import json
import argparse
import sys
from typing import List, Dict, Any

from src.scrapers.citation_scrapers import GoogleScholarScraper
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


def list_papers_with_numbers(papers: List[Dict[str, Any]]):
    """Display papers with numbers for easy selection."""
    print(f"\nFound {len(papers)} papers:")
    print("=" * 80)
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'No title')
        authors = paper.get('authors', [])
        author_names = [author.get('name', '') for author in authors]
        
        print(f"{i:3d}. {title}")
        if author_names:
            print(f"     Authors: {', '.join(author_names[:3])}")
            if len(author_names) > 3:
                print(f"              ... and {len(author_names) - 3} more")
        print(f"     Year: {paper.get('year', 'Unknown')}")
        print()


def get_citations_for_paper(paper_title: str, max_citations: int = 20) -> List[Dict[str, Any]]:
    """Get citations for a specific paper using Google Scholar."""
    print(f"\nFinding citations for: '{paper_title}'")
    print("Using Google Scholar...")
    
    try:
        with GoogleScholarScraper() as scholar:
            citations = scholar.get_citations(paper_title, max_citations)
            
            if citations:
                print(f"Found {len(citations)} citing papers:")
                
                citing_papers = []
                for i, paper in enumerate(citations, 1):
                    citing_paper = {
                        'title': paper.title,
                        'authors': [author.name for author in paper.authors],
                        'year': paper.year,
                        'venue': paper.venue,
                        'url': paper.url,
                        'citation_count': paper.citation_count,
                        'abstract': paper.abstract
                    }
                    citing_papers.append(citing_paper)
                    
                    print(f"{i:3d}. {paper.title}")
                    if paper.authors:
                        author_names = [author.name for author in paper.authors[:3]]
                        print(f"     Authors: {', '.join(author_names)}")
                    print(f"     Year: {paper.year or 'Unknown'}")
                    if paper.citation_count:
                        print(f"     Citations: {paper.citation_count}")
                    print()
                
                return citing_papers
            else:
                print("No citations found.")
                return []
                
    except Exception as e:
        print(f"Error finding citations: {e}")
        return []


def get_references_for_paper(paper_title: str, max_references: int = 20) -> List[Dict[str, Any]]:
    """Get related papers (references) using Google Scholar."""
    print(f"\nFinding related papers for: '{paper_title}'")
    print("Using Google Scholar...")
    
    try:
        with GoogleScholarScraper() as scholar:
            related_papers = scholar.get_related_papers(paper_title, max_references)
            
            if related_papers:
                print(f"Found {len(related_papers)} related papers:")
                
                reference_papers = []
                for i, paper in enumerate(related_papers, 1):
                    ref_paper = {
                        'title': paper.title,
                        'authors': [author.name for author in paper.authors],
                        'year': paper.year,
                        'venue': paper.venue,
                        'url': paper.url,
                        'citation_count': paper.citation_count,
                        'abstract': paper.abstract
                    }
                    reference_papers.append(ref_paper)
                    
                    print(f"{i:3d}. {paper.title}")
                    if paper.authors:
                        author_names = [author.name for author in paper.authors[:3]]
                        print(f"     Authors: {', '.join(author_names)}")
                    print(f"     Year: {paper.year or 'Unknown'}")
                    if paper.citation_count:
                        print(f"     Citations: {paper.citation_count}")
                    print()
                
                return reference_papers
            else:
                print("No related papers found.")
                return []
                
    except Exception as e:
        print(f"Error finding related papers: {e}")
        return []


def save_results(paper_title: str, citations: List[Dict], references: List[Dict]):
    """Save citation results to files."""
    storage = StorageManager()
    
    # Create safe filename
    safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')[:50]
    
    if citations:
        citations_file = storage.output_dir / f"{safe_title}_citations.json"
        with open(citations_file, 'w', encoding='utf-8') as f:
            json.dump({
                'paper_title': paper_title,
                'citations_count': len(citations),
                'citations': citations
            }, f, indent=2, ensure_ascii=False)
        print(f"Citations saved to: {citations_file}")
    
    if references:
        references_file = storage.output_dir / f"{safe_title}_references.json"
        with open(references_file, 'w', encoding='utf-8') as f:
            json.dump({
                'paper_title': paper_title,
                'references_count': len(references),
                'references': references
            }, f, indent=2, ensure_ascii=False)
        print(f"References saved to: {references_file}")


def interactive_mode(papers: List[Dict[str, Any]]):
    """Interactive mode for selecting papers."""
    while True:
        print("\nOptions:")
        print("1. Show all papers")
        print("2. Find citations for a paper")
        print("3. Find references for a paper")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            list_papers_with_numbers(papers)
            
        elif choice == '2':
            try:
                paper_num = int(input("Enter paper number for citations: "))
                if 1 <= paper_num <= len(papers):
                    selected_paper = papers[paper_num - 1]
                    paper_title = selected_paper['title']
                    citations = get_citations_for_paper(paper_title)
                    if citations:
                        save_results(paper_title, citations, [])
                else:
                    print("Invalid paper number!")
            except ValueError:
                print("Please enter a valid number!")
                
        elif choice == '3':
            try:
                paper_num = int(input("Enter paper number for references: "))
                if 1 <= paper_num <= len(papers):
                    selected_paper = papers[paper_num - 1]
                    paper_title = selected_paper['title']
                    references = get_references_for_paper(paper_title)
                    if references:
                        save_results(paper_title, [], references)
                else:
                    print("Invalid paper number!")
            except ValueError:
                print("Please enter a valid number!")
                
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please enter 1-4.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Simple Citation Finder - Manual citation lookup tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file output/ICSE_2014.json
  %(prog)s --file output/ICSE_2014.json --paper 5 --citations
  %(prog)s --file output/ICSE_2014.json --paper 5 --references
        """
    )
    
    parser.add_argument('--file', required=True, metavar='PATH',
                       help='Conference JSON file (e.g., output/ICSE_2014.json)')
    parser.add_argument('--paper', type=int, metavar='NUMBER',
                       help='Paper number to get citations/references for')
    parser.add_argument('--citations', action='store_true',
                       help='Get citations for the specified paper')
    parser.add_argument('--references', action='store_true',
                       help='Get references for the specified paper')
    parser.add_argument('--list', action='store_true',
                       help='Just list all papers with numbers')
    parser.add_argument('--max-papers', type=int, default=20,
                       help='Maximum papers to fetch (default: 20)')
    
    args = parser.parse_args()
    
    # Load papers from conference file
    papers = load_conference_papers(args.file)
    if not papers:
        print("No papers found in the file!")
        sys.exit(1)
    
    # Handle different modes
    if args.list:
        list_papers_with_numbers(papers)
        
    elif args.paper:
        if not (1 <= args.paper <= len(papers)):
            print(f"Invalid paper number! Must be between 1 and {len(papers)}")
            sys.exit(1)
            
        selected_paper = papers[args.paper - 1]
        paper_title = selected_paper['title']
        
        print(f"Selected paper #{args.paper}:")
        print(f"Title: {paper_title}")
        print(f"Authors: {', '.join([author.get('name', '') for author in selected_paper.get('authors', [])])}")
        print(f"Year: {selected_paper.get('year', 'Unknown')}")
        
        citations = []
        references = []
        
        if args.citations:
            citations = get_citations_for_paper(paper_title, args.max_papers)
            
        if args.references:
            references = get_references_for_paper(paper_title, args.max_papers)
            
        if citations or references:
            save_results(paper_title, citations, references)
            
    else:
        # Interactive mode
        print(f"Loaded {len(papers)} papers from {args.file}")
        interactive_mode(papers)


if __name__ == '__main__':
    main()