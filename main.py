#!/usr/bin/env python3
"""
PaperHelper - A tool for scraping paper information from top conferences.

This tool scrapes paper information from top (A*) conferences in:
- Software Engineering (SE)
- Artificial Intelligence/Machine Learning (AI/ML) 
- Natural Language Processing (NLP)
"""

import argparse
import logging
import sys
from typing import List, Optional
from datetime import datetime

from src.scrapers import ScraperFactory
from src.scrapers.citation_scrapers import CitationAggregator
from src.utils import StorageManager, DataExporter, PaperFilter, PaperSearcher, PaperAnalyzer
from src.utils.citation_utils import CitationAnalyzer, CitationTracker, CitationRecommender
from config.conferences import CONFERENCES


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('paperhelper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def list_conferences():
    """List all available conferences."""
    print("Available conferences:")
    print("=" * 50)
    
    for domain, conferences in CONFERENCES.items():
        print(f"\n{domain}:")
        for acronym, info in conferences.items():
            print(f"  {acronym}: {info['name']}")
            print(f"    Type: {info['type']}")


def scrape_conference(conference_key: str, year: int, output_format: str = 'json'):
    """Scrape a specific conference for a given year."""
    # Find conference configuration
    conference_config = None
    conference_acronym = None
    
    for domain, conferences in CONFERENCES.items():
        if conference_key.upper() in conferences:
            conference_config = conferences[conference_key.upper()]
            conference_acronym = conference_key.upper()
            break
    
    if not conference_config:
        print(f"Conference '{conference_key}' not found.")
        print("Use --list-conferences to see available conferences.")
        return
    
    print(f"Scraping {conference_config['name']} ({conference_acronym}) for year {year}")
    
    try:
        # Create scraper
        scraper = ScraperFactory.create_scraper(conference_config)
        
        # Scrape papers
        with scraper:
            papers = scraper.scrape_papers(year)
        
        if not papers:
            print(f"No papers found for {conference_acronym} {year}")
            return
        
        print(f"Found {len(papers)} papers")
        
        # Save results
        storage = StorageManager()
        filename = f"{conference_acronym}_{year}"
        file_path = storage.save_papers(papers, filename, output_format)
        
        print(f"Results saved to: {file_path}")
        
        # Print summary
        print_summary(papers)
        
    except Exception as e:
        logging.error(f"Error scraping {conference_acronym} {year}: {e}")
        print(f"Error: {e}")


def scrape_multiple_years(conference_key: str, start_year: int, end_year: int, output_format: str = 'json'):
    """Scrape a conference for multiple years."""
    for year in range(start_year, end_year + 1):
        print(f"\nScraping year {year}...")
        scrape_conference(conference_key, year, output_format)


def scrape_all_conferences(year: int, output_format: str = 'json'):
    """Scrape all conferences for a given year."""
    all_papers = []
    
    for domain, conferences in CONFERENCES.items():
        print(f"\nScraping {domain} conferences for {year}...")
        
        for acronym, config in conferences.items():
            try:
                scraper = ScraperFactory.create_scraper(config)
                
                with scraper:
                    papers = scraper.scrape_papers(year)
                
                if papers:
                    all_papers.extend(papers)
                    print(f"  {acronym}: {len(papers)} papers")
                else:
                    print(f"  {acronym}: No papers found")
                    
            except Exception as e:
                logging.error(f"Error scraping {acronym}: {e}")
                print(f"  {acronym}: Error - {e}")
    
    if all_papers:
        # Save combined results
        storage = StorageManager()
        filename = f"all_conferences_{year}"
        file_path = storage.save_papers(all_papers, filename, output_format)
        
        print(f"\nCombined results saved to: {file_path}")
        print(f"Total papers scraped: {len(all_papers)}")
        
        # Print analysis
        analyzer = PaperAnalyzer(all_papers)
        venue_dist = analyzer.get_venue_distribution()
        
        print("\nPapers by venue:")
        for venue, count in list(venue_dist.items())[:10]:
            print(f"  {venue}: {count}")


def search_papers(query: str, data_file: str):
    """Search through previously scraped papers."""
    try:
        storage = StorageManager()
        paper_data = storage.load_papers(data_file)
        
        # Convert to Paper objects (simplified - you might want to implement proper deserialization)
        print(f"Searching in {len(paper_data)} papers for: '{query}'")
        
        # This is a simplified search - in practice you'd convert back to Paper objects
        matching_papers = []
        for paper_dict in paper_data:
            title = paper_dict.get('title', '').lower()
            abstract = paper_dict.get('abstract', '').lower() if paper_dict.get('abstract') else ''
            
            if query.lower() in title or query.lower() in abstract:
                matching_papers.append(paper_dict)
        
        print(f"Found {len(matching_papers)} matching papers:")
        for i, paper in enumerate(matching_papers[:10], 1):
            print(f"{i}. {paper.get('title', 'No title')}")
            if paper.get('authors'):
                authors = [author.get('name', '') for author in paper['authors']]
                print(f"   Authors: {', '.join(authors)}")
            print(f"   Year: {paper.get('year', 'Unknown')}")
            print()
        
        if len(matching_papers) > 10:
            print(f"... and {len(matching_papers) - 10} more")
            
    except Exception as e:
        print(f"Error searching papers: {e}")


def find_paper_citations(title: str, max_papers: int = 50, output_format: str = 'json', use_google_scholar: bool = True):
    """Find citations and references for a given paper title."""
    print(f"Finding citations and references for: '{title}'")
    if use_google_scholar:
        print("Using Google Scholar for enhanced citation extraction...")
    
    try:
        # Initialize citation aggregator
        aggregator = CitationAggregator()
        
        # Get citation network with Google Scholar option
        central_paper, citations, references = aggregator.find_paper_citations(title, max_papers, use_google_scholar)
        
        if not central_paper:
            print(f"Could not find paper: '{title}'")
            return
        
        # Create citation network
        from src.models.paper import CitationNetwork
        network = CitationNetwork(
            central_paper=central_paper,
            citations=citations,
            references=references,
            depth=1
        )
        
        print(f"Found paper: {network.central_paper.title}")
        print(f"Year: {network.central_paper.year}")
        print(f"Citations found: {len(network.citations)}")
        print(f"References found: {len(network.references)}")
        
        # Save citation network
        storage = StorageManager()
        tracker = CitationTracker(storage)
        
        # Create safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        network_file = tracker.save_citation_network(network, safe_title)
        print(f"Citation network saved to: {network_file}")
        
        # Save individual lists
        if network.citations:
            citations_file = storage.save_papers(network.citations, f"{safe_title}_citations", output_format)
            print(f"Citations saved to: {citations_file}")
        
        if network.references:
            references_file = storage.save_papers(network.references, f"{safe_title}_references", output_format)
            print(f"References saved to: {references_file}")
        
        # Generate analysis
        analyzer = CitationAnalyzer()
        analysis = analyzer.analyze_citation_network(network)
        
        print_citation_analysis(analysis)
        
        # Export graph visualization
        try:
            graph_file = tracker.export_citation_graph(network, 'json')
            print(f"Citation graph exported to: {graph_file}")
        except Exception as e:
            print(f"Warning: Could not export graph: {e}")
        
    except Exception as e:
        logging.error(f"Error finding citations for '{title}': {e}")
        print(f"Error: {e}")


def print_citation_analysis(analysis: dict):
    """Print citation analysis results."""
    print("\n" + "=" * 60)
    print("CITATION ANALYSIS")
    print("=" * 60)
    
    # Basic stats
    stats = analysis['network_stats']
    print(f"Total papers in network: {stats['total_papers']}")
    print(f"Citations: {stats['citations_found']}")
    print(f"References: {stats['references_found']}")
    print(f"Citation/Reference ratio: {stats['citation_ratio']:.2f}")
    
    # Temporal analysis
    temporal = analysis['temporal_analysis']
    if temporal['reference_years']['avg_age']:
        print(f"Average age of references: {temporal['reference_years']['avg_age']:.1f} years")
    if temporal['citation_years']['years_since_publication']:
        print(f"Years since publication: {temporal['citation_years']['years_since_publication']} years")
    
    # Venue analysis
    venue = analysis['venue_analysis']
    print(f"\nCentral paper venue: {venue['central_venue']}")
    
    if venue['reference_venues']:
        print("\nTop venues in references:")
        for venue_name, count in list(venue['reference_venues'].items())[:5]:
            print(f"  {venue_name}: {count} papers")
    
    if venue['citation_venues']:
        print("\nTop venues citing this paper:")
        for venue_name, count in list(venue['citation_venues'].items())[:5]:
            print(f"  {venue_name}: {count} papers")
    
    # Author analysis
    author = analysis['author_analysis']
    if author['top_citing_authors']:
        print("\nTop citing authors:")
        for author_name, count in list(author['top_citing_authors'].items())[:5]:
            print(f"  {author_name}: {count} papers")
    
    if author['potential_collaborators']:
        print(f"\nPotential collaborators: {len(author['potential_collaborators'])}")
        for collaborator in list(author['potential_collaborators'])[:5]:
            print(f"  {collaborator}")
    
    # Impact metrics
    impact = analysis['impact_metrics']
    print(f"\nImpact metrics:")
    print(f"  Direct citations: {impact['direct_citations']}")
    print(f"  References made: {impact['references_made']}")
    print(f"  Network total citations: {impact['network_total_citations']}")
    print(f"  Influence score: {impact['influence_score']:.2f}")


def recommend_related_papers(title: str, max_recommendations: int = 10):
    """Recommend related papers based on citation analysis."""
    print(f"Finding recommendations for: '{title}'")
    
    try:
        # Get citation network
        aggregator = CitationAggregator()
        network = aggregator.get_enriched_citation_network(title)
        
        if not network:
            print(f"Could not find paper: '{title}'")
            return
        
        # Generate recommendations
        recommender = CitationRecommender()
        recommendations = recommender.recommend_papers_to_cite(network, max_recommendations)
        collaborators = recommender.find_potential_collaborators(network)
        
        print(f"\nRecommended papers to cite ({len(recommendations)}):")
        for i, paper in enumerate(recommendations, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(author.name for author in paper.authors[:3])}")
            print(f"   Year: {paper.year}, Citations: {paper.citation_count or 0}")
            if paper.venue:
                print(f"   Venue: {paper.venue}")
            print()
        
        if collaborators:
            print(f"Potential collaborators ({len(collaborators)}):")
            for collab in collaborators[:5]:
                print(f"• {collab['name']}: {collab['papers_count']} citing papers, {collab['total_citations']} total citations")
                if collab['venues']:
                    print(f"  Recent venues: {', '.join(collab['venues'][:3])}")
                print()
        
    except Exception as e:
        logging.error(f"Error generating recommendations for '{title}': {e}")
        print(f"Error: {e}")


def print_summary(papers):
    """Print summary statistics of scraped papers."""
    if not papers:
        return
    
    analyzer = PaperAnalyzer(papers)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    print(f"Total papers: {len(papers)}")
    
    # Year distribution
    year_dist = analyzer.get_yearly_distribution()
    if year_dist:
        print(f"Years covered: {min(year_dist.keys())} - {max(year_dist.keys())}")
    
    # Author statistics
    top_authors = analyzer.get_top_authors(5)
    if top_authors:
        print("\nTop authors:")
        for author, count in top_authors:
            print(f"  {author}: {count} papers")
    
    # Keyword statistics
    common_keywords = analyzer.get_common_keywords(10)
    if common_keywords:
        print("\nCommon keywords:")
        for keyword, count in common_keywords:
            print(f"  {keyword}: {count} papers")
    
    # Citation statistics
    citation_stats = analyzer.get_citation_stats()
    if citation_stats:
        print(f"\nCitation statistics:")
        print(f"  Papers with citations: {citation_stats['total_papers_with_citations']}")
        print(f"  Average citations: {citation_stats['average_citations']:.1f}")
        print(f"  Max citations: {citation_stats['max_citations']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PaperHelper - Scrape papers from top conferences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-conferences
  %(prog)s --scrape ICSE --year 2023
  %(prog)s --scrape ICML --year-range 2020 2023 --format csv
  %(prog)s --scrape-all --year 2023
  %(prog)s --search "machine learning" --file output/ICML_2023.json
  %(prog)s --citations "Deep Learning for Software Engineering"
  %(prog)s --recommend "Attention Is All You Need" --max-papers 20
        """
    )
    
    # Main actions
    parser.add_argument('--list-conferences', action='store_true',
                       help='List all available conferences')
    parser.add_argument('--scrape', metavar='CONFERENCE',
                       help='Scrape specific conference (e.g., ICSE, ICML, ACL)')
    parser.add_argument('--scrape-all', action='store_true',
                       help='Scrape all conferences')
    parser.add_argument('--search', metavar='QUERY',
                       help='Search through scraped papers')
    parser.add_argument('--citations', metavar='TITLE',
                       help='Find citations and references for a paper title')
    parser.add_argument('--recommend', metavar='TITLE',
                       help='Get paper recommendations based on citation analysis')
    
    # Options
    parser.add_argument('--year', type=int, default=datetime.now().year - 1,
                       help='Year to scrape (default: last year)')
    parser.add_argument('--year-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Year range to scrape (inclusive)')
    parser.add_argument('--format', choices=['json', 'csv', 'bibtex'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--file', metavar='PATH',
                       help='File path for search operations')
    parser.add_argument('--max-papers', type=int, default=50,
                       help='Maximum number of papers to fetch for citations (default: 50)')
    parser.add_argument('--use-scholar', action='store_true', default=True,
                       help='Use Google Scholar for citation extraction (default: enabled)')
    parser.add_argument('--no-scholar', action='store_true',
                       help='Disable Google Scholar and use only APIs')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle arguments
    if args.list_conferences:
        list_conferences()
    
    elif args.scrape:
        if args.year_range:
            scrape_multiple_years(args.scrape, args.year_range[0], args.year_range[1], args.format)
        else:
            scrape_conference(args.scrape, args.year, args.format)
    
    elif args.scrape_all:
        scrape_all_conferences(args.year, args.format)
    
    elif args.search:
        if not args.file:
            print("Error: --file is required for search operations")
            sys.exit(1)
        search_papers(args.search, args.file)
    
    elif args.citations:
        use_scholar = args.use_scholar and not args.no_scholar
        find_paper_citations(args.citations, args.max_papers, args.format, use_scholar)
    
    elif args.recommend:
        recommend_related_papers(args.recommend, args.max_papers)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()