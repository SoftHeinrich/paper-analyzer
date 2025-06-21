"""
Conference history and predecessor mappings for comprehensive historical testing.
Tracks conference name changes, mergers, and splits over the past 15 years (2009-2024).
"""

from typing import Dict, List, Tuple, Optional

# Conference history mappings: current_name -> [(year_range, venue_key, venue_short)]
CONFERENCE_HISTORY = {
    # Software Engineering Conferences
    'SANER': [
        # SANER started in 2015, before that it was CSMR and WCRE
        (2015, 2024, 'conf/wcre', 'saner'),      # SANER (2015-present)
    ],
    
    'ICSME': [
        # ICSME started in 2014, before that it was ICSM
        (2014, 2024, 'conf/icsm', 'icsme'),     # ICSME (2014-present)
    ],
    
    'ICPC': [
        # ICPC was always ICPC but had different venue keys in DBLP
        (2009, 2024, 'conf/iwpc', 'icpc'),      # Always ICPC, but DBLP uses IWPC
    ],
    
    'ASE': [
        # ASE was always ASE but had venue key changes
        (2009, 2024, 'conf/kbse', 'ase'),       # ASE (DBLP uses KBSE - Knowledge-Based Software Engineering)
    ],
    
    'FSE': [
        # FSE was ESEC/FSE in some years
        (2009, 2024, 'conf/sigsoft', 'fse'),    # FSE/ESEC-FSE
    ],
    
    'ICSE': [
        (2009, 2024, 'conf/icse', 'icse'),      # ICSE has been consistent
    ],
    
    'ISSTA': [
        (2009, 2024, 'conf/issta', 'issta'),    # ISSTA has been consistent
    ],
    
    'MSR': [
        (2009, 2024, 'conf/msr', 'msr'),        # MSR started in 2004, consistent since
    ],
    
    'ICSA': [
        # ICSA started in 2017, before that it was WICSA/QoSA/CompArch
        (2017, 2024, 'conf/icsa', 'icsa'),      # ICSA (2017-present)
    ],
    
    'ECSA': [
        (2009, 2024, 'conf/ecsa', 'ecsa'),      # ECSA has been consistent since 2007
    ],
    
    'OOPSLA': [
        (2009, 2024, 'conf/oopsla', 'oopsla'),  # OOPSLA has been consistent
    ],
    
    'RE': [
        (2009, 2024, 'conf/re', 're'),          # RE has been consistent
    ],
    
    'ISSRE': [
        (2009, 2024, 'conf/issre', 'issre'),    # ISSRE has been consistent
    ],
    
    # AI/ML Conferences
    'ICML': [
        (2009, 2024, 'conf/icml', 'icml'),      # ICML has been consistent
    ],
    
    'NIPS': [
        # NeurIPS was called NIPS until 2017, but uses same venue
        (2009, 2024, 'conf/nips', 'neurips'),   # NIPS/NeurIPS (uses neurips in DBLP)
    ],
    
    'ICLR': [
        # ICLR started in 2013
        (2013, 2024, 'conf/iclr', 'iclr'),      # ICLR (2013-present)
    ],
    
    'AAAI': [
        (2009, 2024, 'conf/aaai', 'aaai'),      # AAAI has been consistent
    ],
    
    'IJCAI': [
        (2009, 2024, 'conf/ijcai', 'ijcai'),    # IJCAI has been consistent
    ],
    
    # NLP Conferences
    'ACL': [
        (2009, 2024, 'venues/acl', 'acl'),      # ACL has been consistent
    ],
    
    'EMNLP': [
        (2009, 2024, 'venues/emnlp', 'emnlp'),  # EMNLP has been consistent
    ],
    
    'NAACL': [
        # NAACL happens every 2-3 years
        (2009, 2024, 'venues/naacl', 'naacl'),  # NAACL (not every year)
    ],
    
    'COLING': [
        # COLING happens every 2 years
        (2009, 2024, 'venues/coling', 'coling'), # COLING (every 2 years)
    ],
}

# Years when conferences didn't happen or had different names
CONFERENCE_GAPS = {
    'ICLR': [2009, 2010, 2011, 2012],  # ICLR started in 2013
    'SANER': [2009, 2010, 2011, 2012, 2013, 2014],  # SANER started in 2015
    'ICSME': [2009, 2010, 2011, 2012, 2013],  # ICSME started in 2014
    'ICSA': [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],  # ICSA started in 2017
    'NAACL': [2011, 2014, 2017, 2020, 2023],  # NAACL skipped years (approximate)
    'COLING': [2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023],  # COLING every 2 years
}

# Expected minimum paper counts by year range (accounting for conference growth)
HISTORICAL_MIN_PAPERS = {
    # SE Conferences
    'ICSE': {(2009, 2014): 80, (2015, 2019): 100, (2020, 2024): 120},
    'FSE': {(2009, 2014): 60, (2015, 2019): 80, (2020, 2024): 100},
    'ASE': {(2009, 2014): 40, (2015, 2019): 60, (2020, 2024): 80},
    'ISSTA': {(2009, 2014): 15, (2015, 2019): 20, (2020, 2024): 25},
    'MSR': {(2009, 2014): 15, (2015, 2019): 25, (2020, 2024): 30},
    'ICPC': {(2009, 2014): 10, (2015, 2019): 15, (2020, 2024): 20},
    'ICSME': {(2009, 2014): 25, (2015, 2019): 35, (2020, 2024): 45},
    'SANER': {(2009, 2014): 20, (2015, 2019): 30, (2020, 2024): 40},
    'ICSA': {(2009, 2014): 8, (2015, 2019): 12, (2020, 2024): 15},
    'ECSA': {(2009, 2014): 8, (2015, 2019): 12, (2020, 2024): 15},
    'OOPSLA': {(2009, 2014): 25, (2015, 2019): 35, (2020, 2024): 45},
    'RE': {(2009, 2014): 15, (2015, 2019): 20, (2020, 2024): 25},
    'ISSRE': {(2009, 2014): 10, (2015, 2019): 15, (2020, 2024): 20},
    
    # AI/ML Conferences  
    'ICML': {(2009, 2014): 200, (2015, 2019): 400, (2020, 2024): 800},
    'NIPS': {(2009, 2014): 300, (2015, 2019): 600, (2020, 2024): 1200},
    'ICLR': {(2013, 2016): 100, (2017, 2019): 300, (2020, 2024): 600},
    'AAAI': {(2009, 2014): 200, (2015, 2019): 400, (2020, 2024): 800},
    'IJCAI': {(2009, 2014): 150, (2015, 2019): 250, (2020, 2024): 400},
    
    # NLP Conferences
    'ACL': {(2009, 2014): 150, (2015, 2019): 250, (2020, 2024): 400},
    'EMNLP': {(2009, 2014): 150, (2015, 2019): 250, (2020, 2024): 400},
    'NAACL': {(2009, 2014): 80, (2015, 2019): 120, (2020, 2024): 200},
    'COLING': {(2009, 2014): 150, (2015, 2019): 200, (2020, 2024): 300},
}


def get_venue_for_year(conference: str, year: int) -> Tuple[str, str]:
    """
    Get the appropriate venue_key and venue_short for a conference in a specific year.
    
    Args:
        conference: Conference name (e.g., 'SANER', 'ICSME')
        year: Year to check
        
    Returns:
        Tuple of (venue_key, venue_short) for that year
    """
    if conference not in CONFERENCE_HISTORY:
        raise ValueError(f"Conference {conference} not found in history")
    
    history = CONFERENCE_HISTORY[conference]
    
    for start_year, end_year, venue_key, venue_short in history:
        if start_year <= year <= end_year:
            return venue_key, venue_short
    
    raise ValueError(f"No venue mapping found for {conference} in year {year}")


def get_expected_min_papers(conference: str, year: int) -> int:
    """
    Get expected minimum paper count for a conference in a specific year.
    
    Args:
        conference: Conference name
        year: Year to check
        
    Returns:
        Expected minimum number of papers
    """
    if conference not in HISTORICAL_MIN_PAPERS:
        return 5  # Default minimum
    
    ranges = HISTORICAL_MIN_PAPERS[conference]
    
    for (start_year, end_year), min_papers in ranges.items():
        if start_year <= year <= end_year:
            return min_papers
    
    return 5  # Default minimum


def conference_exists_in_year(conference: str, year: int) -> bool:
    """
    Check if a conference existed/happened in a specific year.
    
    Args:
        conference: Conference name
        year: Year to check
        
    Returns:
        True if conference happened in that year
    """
    # Check if conference is in gaps (didn't happen that year)
    if conference in CONFERENCE_GAPS:
        if year in CONFERENCE_GAPS[conference]:
            return False
    
    # Check if conference existed at all in that year
    try:
        get_venue_for_year(conference, year)
        return True
    except ValueError:
        return False


def get_all_test_years() -> List[int]:
    """Get all years for comprehensive testing (2009-2024)."""
    return list(range(2009, 2025))


def get_all_conferences() -> List[str]:
    """Get all conference names."""
    return list(CONFERENCE_HISTORY.keys())


def get_predecessor_conferences(conference: str) -> List[str]:
    """
    Get list of predecessor conference names for historical research.
    
    Args:
        conference: Current conference name
        
    Returns:
        List of predecessor conference short names
    """
    predecessors = []
    
    if conference == 'SANER':
        predecessors = ['wcre', 'csmr']
    elif conference == 'ICSME':
        predecessors = ['icsm']
    elif conference == 'ICSA':
        predecessors = ['wicsa']
    
    return predecessors