# PaperHelper

A comprehensive tool for scraping paper information from top (A*) conferences in Software Engineering, AI/ML, and Natural Language Processing.

## Features

- **Multi-domain Coverage**: Scrapes from top conferences in:
  - Software Engineering (ICSE, FSE, ASE, ISSTA)
  - AI/Machine Learning (ICML, NIPS, ICLR, AAAI, IJCAI)
  - Natural Language Processing (ACL, EMNLP, NAACL, COLING)

- **Multiple Data Sources**: Supports various academic databases and platforms:
  - DBLP Database
  - OpenReview (ICLR, etc.)
  - ACL Anthology
  - Semantic Scholar API
  - CrossRef API
  - Google Scholar (web scraping)

- **Citation Tracking & Analysis**: 
  - Find papers that cite a given paper
  - Find papers referenced by a given paper
  - Citation network visualization
  - Impact metrics and analysis
  - Collaboration recommendations
  - Related paper suggestions

- **Flexible Output Formats**: Export scraped data in:
  - JSON (structured data)
  - CSV (spreadsheet-friendly)
  - BibTeX (citation management)
  - Excel (with pandas integration)
  - GraphML (network visualization)

- **Advanced Search & Filtering**: 
  - Full-text search across papers
  - Filter by year, venue, author, keywords
  - Citation-based filtering
  - Similarity search

- **Data Analysis**: Built-in analytics for:
  - Yearly publication trends
  - Author productivity analysis
  - Keyword frequency analysis
  - Citation network analysis
  - Impact and influence metrics

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source
```bash
git clone https://github.com/paperhelper/paperhelper.git
cd paperhelper
pip install -r requirements.txt
pip install -e .
```

### Install dependencies only
```bash
pip install -r requirements.txt
```

## Quick Start

### List available conferences
```bash
python main.py --list-conferences
```

### Scrape a specific conference
```bash
# Scrape ICSE 2023
python main.py --scrape ICSE --year 2023

# Scrape ICML papers from 2020-2023 in CSV format
python main.py --scrape ICML --year-range 2020 2023 --format csv

# Scrape all conferences for 2023
python main.py --scrape-all --year 2023
```

### Search through scraped data
```bash
# Search for machine learning papers
python main.py --search "machine learning" --file output/ICML_2023.json

# Find citations and references for a paper
python main.py --citations "Attention Is All You Need"

# Get paper recommendations based on citation analysis
python main.py --recommend "Deep Learning for Software Engineering"
```

## Usage Examples

### Basic Scraping
```python
from src.scrapers import ScraperFactory
from config.conferences import CONFERENCES

# Get ICSE configuration
icse_config = CONFERENCES['SE']['ICSE']

# Create scraper
scraper = ScraperFactory.create_scraper(icse_config)

# Scrape papers
with scraper:
    papers = scraper.scrape_papers(2023)

print(f"Found {len(papers)} papers")
```

### Data Analysis
```python
from src.utils import PaperAnalyzer, StorageManager

# Load previously scraped data
storage = StorageManager()
paper_data = storage.load_papers('output/ICSE_2023.json')

# Analyze trends
analyzer = PaperAnalyzer(papers)
yearly_dist = analyzer.get_yearly_distribution()
top_authors = analyzer.get_top_authors(10)
common_keywords = analyzer.get_common_keywords(20)
```

### Citation Tracking
```python
from src.scrapers.citation_scrapers import CitationAggregator
from src.utils.citation_utils import CitationAnalyzer, CitationRecommender

# Find citations and references for a paper
aggregator = CitationAggregator()
network = aggregator.get_enriched_citation_network("Attention Is All You Need")

print(f"Found {len(network.citations)} citing papers")
print(f"Found {len(network.references)} referenced papers")

# Analyze citation patterns
analyzer = CitationAnalyzer()
analysis = analyzer.analyze_citation_network(network)
print(f"Influence score: {analysis['impact_metrics']['influence_score']}")

# Get recommendations
recommender = CitationRecommender()
recommendations = recommender.recommend_papers_to_cite(network)
collaborators = recommender.find_potential_collaborators(network)
```

### Advanced Filtering
```python
from src.utils import PaperFilter, PaperSearcher

# Filter papers
recent_papers = PaperFilter.by_year_range(papers, 2020, 2023)
ai_papers = PaperFilter.by_keyword(papers, "artificial intelligence")
highly_cited = PaperFilter.by_citation_count(papers, min_citations=50)

# Search functionality
searcher = PaperSearcher(papers)
relevant_papers = searcher.search("deep learning transformers")
```

## Project Structure

```
PaperHelper/
├── main.py                 # Main application entry point
├── config/
│   ├── __init__.py
│   └── conferences.py      # Conference configurations
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── paper.py        # Data models & citation networks
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py         # Base scraper classes
│   │   ├── dblp_scraper.py # DBLP database scraper
│   │   ├── openreview_scraper.py # OpenReview scraper
│   │   ├── acl_scraper.py  # ACL Anthology scraper
│   │   └── citation_scrapers.py # Citation tracking scrapers
│   └── utils/
│       ├── __init__.py
│       ├── storage.py      # Data storage utilities
│       ├── filters.py      # Search and filter utilities
│       └── citation_utils.py # Citation analysis utilities
├── output/                 # Generated output files
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

## Supported Conferences

### Software Engineering (SE)
- **ICSE**: International Conference on Software Engineering
- **FSE**: ACM SIGSOFT International Symposium on Foundations of Software Engineering
- **ASE**: IEEE/ACM International Conference on Automated Software Engineering
- **ISSTA**: International Symposium on Software Testing and Analysis

### AI/Machine Learning
- **ICML**: International Conference on Machine Learning
- **NIPS**: Conference on Neural Information Processing Systems
- **ICLR**: International Conference on Learning Representations
- **AAAI**: AAAI Conference on Artificial Intelligence
- **IJCAI**: International Joint Conference on Artificial Intelligence

### Natural Language Processing
- **ACL**: Annual Meeting of the Association for Computational Linguistics
- **EMNLP**: Conference on Empirical Methods in Natural Language Processing
- **NAACL**: North American Chapter of the Association for Computational Linguistics
- **COLING**: International Conference on Computational Linguistics

## Configuration

The tool uses configuration files to define:
- Conference URLs and metadata
- Scraper-specific settings
- Rate limiting and request parameters
- Output format preferences

Edit `config/conferences.py` to modify conference settings or add new venues.

## Rate Limiting and Ethics

PaperHelper implements responsible scraping practices:
- Configurable delays between requests
- Respect for robots.txt files
- User-agent identification
- Error handling and retry logic

Please ensure you comply with the terms of service of the websites you're scraping.

## Output Formats

### JSON
Structured data with full paper metadata:
```json
{
  "scraped_at": "2023-12-01T10:30:00",
  "total_papers": 150,
  "papers": [
    {
      "title": "Deep Learning for Software Engineering",
      "authors": [{"name": "John Doe", "affiliation": "University"}],
      "year": 2023,
      "venue": "ICSE",
      "abstract": "...",
      "keywords": ["deep learning", "software engineering"],
      "doi": "10.1109/ICSE.2023.123",
      "url": "https://...",
      "pdf_url": "https://..."
    }
  ]
}
```

### CSV
Tabular format suitable for spreadsheet analysis with columns for title, authors, year, venue, abstract, etc.

### BibTeX
Citation format for reference managers:
```bibtex
@inproceedings{doe2023deep,
  title={Deep Learning for Software Engineering},
  author={John Doe},
  booktitle={International Conference on Software Engineering},
  year={2023},
  doi={10.1109/ICSE.2023.123}
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for academic and research purposes. Please respect the terms of service of the websites you scrape and consider the load on their servers. The authors are not responsible for any misuse of this tool.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the documentation
- Review existing issues for solutions

## Changelog

### Version 1.0.0
- Initial release
- Support for DBLP, OpenReview, and ACL Anthology
- Multiple output formats
- Advanced search and filtering
- Comprehensive documentation