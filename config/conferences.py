"""
Configuration for top conferences in SE, AI/ML, and NLP fields.
"""

CONFERENCES = {
    # Software Engineering (A* conferences)
    'SE': {
        'ICSE': {
            'name': 'International Conference on Software Engineering',
            'base_url': 'https://conf.researchr.org/series/icse',
            'type': 'dblp',
            'venue_key': 'conf/icse',
            'venue_path': 'conf/icse',
            'venue_short': 'icse'
        },
        'FSE': {
            'name': 'ACM SIGSOFT International Symposium on Foundations of Software Engineering',
            'base_url': 'https://conf.researchr.org/series/fse',
            'type': 'dblp',
            'venue_key': 'conf/sigsoft',
            'venue_path': 'conf/sigsoft',
            'venue_short': 'fse'
        },
        'ASE': {
            'name': 'IEEE/ACM International Conference on Automated Software Engineering',
            'base_url': 'https://conf.researchr.org/series/ase',
            'type': 'dblp',
            'venue_key': 'conf/kbse',
            'venue_path': 'conf/kbse',
            'venue_short': 'ase'
        },
        'ISSTA': {
            'name': 'International Symposium on Software Testing and Analysis',
            'base_url': 'https://conf.researchr.org/series/issta',
            'type': 'dblp',
            'venue_key': 'conf/issta',
            'venue_path': 'conf/issta',
            'venue_short': 'issta'
        },
        'ICSA': {
            'name': 'International Conference on Software Architecture',
            'base_url': 'https://conf.researchr.org/series/icsa',
            'type': 'dblp',
            'venue_key': 'conf/icsa',
            'venue_path': 'conf/icsa',
            'venue_short': 'icsa'
        },
        'MSR': {
            'name': 'International Conference on Mining Software Repositories',
            'base_url': 'https://conf.researchr.org/series/msr',
            'type': 'dblp',
            'venue_key': 'conf/msr',
            'venue_path': 'conf/msr',
            'venue_short': 'msr'
        },
        'ICPC': {
            'name': 'IEEE International Conference on Program Comprehension',
            'base_url': 'https://conf.researchr.org/series/icpc',
            'type': 'dblp',
            'venue_key': 'conf/iwpc',
            'venue_path': 'conf/iwpc',
            'venue_short': 'icpc'
        },
        'ICSME': {
            'name': 'IEEE International Conference on Software Maintenance and Evolution',
            'base_url': 'https://conf.researchr.org/series/icsme',
            'type': 'dblp',
            'venue_key': 'conf/icsm',
            'venue_path': 'conf/icsm',
            'venue_short': 'icsme'
        },
        'SANER': {
            'name': 'IEEE International Conference on Software Analysis, Evolution and Reengineering',
            'base_url': 'https://conf.researchr.org/series/saner',
            'type': 'dblp',
            'venue_key': 'conf/wcre',
            'venue_path': 'conf/wcre',
            'venue_short': 'saner'
        },
        'ECSA': {
            'name': 'European Conference on Software Architecture',
            'base_url': 'https://conf.researchr.org/series/ecsa',
            'type': 'dblp',
            'venue_key': 'conf/ecsa',
            'venue_path': 'conf/ecsa',
            'venue_short': 'ecsa'
        },
        'OOPSLA': {
            'name': 'ACM Conference on Object-Oriented Programming, Systems, Languages, and Applications',
            'base_url': 'https://conf.researchr.org/series/splash',
            'type': 'dblp',
            'venue_key': 'conf/oopsla',
            'venue_path': 'conf/oopsla',
            'venue_short': 'oopsla'
        },
        'RE': {
            'name': 'IEEE International Requirements Engineering Conference',
            'base_url': 'https://conf.researchr.org/series/RE',
            'type': 'dblp',
            'venue_key': 'conf/re',
            'venue_path': 'conf/re',
            'venue_short': 're'
        },
        'ISSRE': {
            'name': 'IEEE International Symposium on Software Reliability Engineering',
            'base_url': 'https://conf.researchr.org/series/issre',
            'type': 'dblp',
            'venue_key': 'conf/issre',
            'venue_path': 'conf/issre',
            'venue_short': 'issre'
        }
    },
    
    # AI/ML (A* conferences)
    'AI_ML': {
        'ICML': {
            'name': 'International Conference on Machine Learning',
            'base_url': 'https://icml.cc',
            'type': 'dblp',
            'venue_key': 'conf/icml',
            'venue_path': 'conf/icml',
            'venue_short': 'icml'
        },
        'NIPS': {
            'name': 'Conference on Neural Information Processing Systems',
            'base_url': 'https://neurips.cc',
            'type': 'dblp',
            'venue_key': 'conf/nips',
            'venue_path': 'conf/nips',
            'venue_short': 'neurips'
        },
        'ICLR': {
            'name': 'International Conference on Learning Representations',
            'base_url': 'https://iclr.cc',
            'type': 'dblp',
            'venue_key': 'conf/iclr',
            'venue_path': 'conf/iclr',
            'venue_short': 'iclr',
            'track_types': ['oral', 'spotlight', 'poster']
        },
        'AAAI': {
            'name': 'AAAI Conference on Artificial Intelligence',
            'base_url': 'https://aaai.org',
            'type': 'dblp',
            'venue_key': 'conf/aaai',
            'venue_path': 'conf/aaai',
            'venue_short': 'aaai'
        },
        'IJCAI': {
            'name': 'International Joint Conference on Artificial Intelligence',
            'base_url': 'https://ijcai.org',
            'type': 'dblp',
            'venue_key': 'conf/ijcai',
            'venue_path': 'conf/ijcai',
            'venue_short': 'ijcai'
        }
    },
    
    # NLP (A* conferences)
    'NLP': {
        'ACL': {
            'name': 'Annual Meeting of the Association for Computational Linguistics',
            'base_url': 'https://aclweb.org',
            'type': 'anthology',
            'venue_key': 'venues/acl',
            'venue_short': 'acl'
        },
        'EMNLP': {
            'name': 'Conference on Empirical Methods in Natural Language Processing',
            'base_url': 'https://aclweb.org',
            'type': 'anthology',
            'venue_key': 'venues/emnlp',
            'venue_short': 'emnlp'
        },
        'NAACL': {
            'name': 'North American Chapter of the Association for Computational Linguistics',
            'base_url': 'https://aclweb.org',
            'type': 'anthology',
            'venue_key': 'venues/naacl',
            'venue_short': 'naacl'
        },
        'COLING': {
            'name': 'International Conference on Computational Linguistics',
            'base_url': 'https://aclweb.org',
            'type': 'anthology',
            'venue_key': 'venues/coling',
            'venue_short': 'coling'
        }
    }
}

SCRAPER_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'request_delay': 1.0,  # seconds between requests
    'timeout': 30,
    'max_retries': 3,
    'output_formats': ['json', 'csv', 'bibtex'],
    'default_year_range': 5  # last 5 years by default
}

DBLP_CONFIG = {
    'base_url': 'https://dblp.org/search/publ/api',
    'xml_url': 'https://dblp.org/db/{venue_path}/{venue_short}{year}.xml'
}

OPENREVIEW_CONFIG = {
    'base_url': 'https://api.openreview.net',
    'notes_endpoint': '/notes'
}

ACL_ANTHOLOGY_CONFIG = {
    'base_url': 'https://aclanthology.org',
    'api_base': 'https://aclanthology.org/anthology+bib'
}