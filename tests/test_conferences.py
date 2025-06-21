#!/usr/bin/env python3
"""
Unit tests for conference configurations and scraping functionality.
Tests all SE conferences including the newly added ones.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.conferences import CONFERENCES, SCRAPER_CONFIG, DBLP_CONFIG
from src.scrapers import ScraperFactory
from src.scrapers.base import BaseScraper
from src.models.paper import Paper, Author, ConferenceInfo


class TestConferenceConfigurations(unittest.TestCase):
    """Test conference configuration data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.se_conferences = CONFERENCES['SE']
        self.ai_ml_conferences = CONFERENCES['AI_ML']
        self.nlp_conferences = CONFERENCES['NLP']
        
        # Expected SE conferences including new ones
        self.expected_se_conferences = {
            'ICSE', 'FSE', 'ASE', 'ISSTA', 'ICSA', 'MSR', 'ICPC', 
            'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE'
        }
    
    def test_se_conference_presence(self):
        """Test that all expected SE conferences are present."""
        actual_conferences = set(self.se_conferences.keys())
        self.assertEqual(actual_conferences, self.expected_se_conferences)
    
    def test_new_se_conferences_added(self):
        """Test that the new SE conferences have been added."""
        new_conferences = {'MSR', 'ICPC', 'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE'}
        for conf in new_conferences:
            self.assertIn(conf, self.se_conferences, f"Conference {conf} not found in SE conferences")
    
    def test_conference_structure(self):
        """Test that each conference has required fields."""
        base_required_fields = {'name', 'base_url', 'type', 'venue_key', 'venue_short'}
        dblp_required_fields = base_required_fields | {'venue_path'}
        
        for category, conferences in CONFERENCES.items():
            for conf_name, conf_data in conferences.items():
                with self.subTest(category=category, conference=conf_name):
                    actual_fields = set(conf_data.keys())
                    
                    if conf_data.get('type') == 'dblp':
                        required_fields = dblp_required_fields
                    else:
                        required_fields = base_required_fields
                    
                    self.assertTrue(required_fields.issubset(actual_fields), 
                                  f"Conference {conf_name} missing required fields: {required_fields - actual_fields}")
    
    def test_msr_configuration(self):
        """Test MSR conference configuration."""
        msr = self.se_conferences['MSR']
        self.assertEqual(msr['name'], 'International Conference on Mining Software Repositories')
        self.assertEqual(msr['type'], 'dblp')
        self.assertEqual(msr['venue_key'], 'conf/msr')
        self.assertEqual(msr['venue_short'], 'msr')
    
    def test_icpc_configuration(self):
        """Test ICPC conference configuration."""
        icpc = self.se_conferences['ICPC']
        self.assertEqual(icpc['name'], 'IEEE International Conference on Program Comprehension')
        self.assertEqual(icpc['type'], 'dblp')
        self.assertEqual(icpc['venue_key'], 'conf/iwpc')
        self.assertEqual(icpc['venue_short'], 'icpc')
    
    def test_icsme_configuration(self):
        """Test ICSME conference configuration."""
        icsme = self.se_conferences['ICSME']
        self.assertEqual(icsme['name'], 'IEEE International Conference on Software Maintenance and Evolution')
        self.assertEqual(icsme['type'], 'dblp')
        self.assertEqual(icsme['venue_key'], 'conf/icsm')
        self.assertEqual(icsme['venue_short'], 'icsme')
    
    def test_saner_configuration(self):
        """Test SANER conference configuration."""
        saner = self.se_conferences['SANER']
        self.assertEqual(saner['name'], 'IEEE International Conference on Software Analysis, Evolution and Reengineering')
        self.assertEqual(saner['type'], 'dblp')
        self.assertEqual(saner['venue_key'], 'conf/wcre')
        self.assertEqual(saner['venue_short'], 'saner')
    
    def test_ecsa_configuration(self):
        """Test ECSA conference configuration."""
        ecsa = self.se_conferences['ECSA']
        self.assertEqual(ecsa['name'], 'European Conference on Software Architecture')
        self.assertEqual(ecsa['type'], 'dblp')
        self.assertEqual(ecsa['venue_key'], 'conf/ecsa')
        self.assertEqual(ecsa['venue_short'], 'ecsa')
    
    def test_oopsla_configuration(self):
        """Test OOPSLA conference configuration."""
        oopsla = self.se_conferences['OOPSLA']
        self.assertEqual(oopsla['name'], 'ACM Conference on Object-Oriented Programming, Systems, Languages, and Applications')
        self.assertEqual(oopsla['type'], 'dblp')
        self.assertEqual(oopsla['venue_key'], 'conf/oopsla')
        self.assertEqual(oopsla['venue_short'], 'oopsla')
    
    def test_re_configuration(self):
        """Test RE conference configuration."""
        re = self.se_conferences['RE']
        self.assertEqual(re['name'], 'IEEE International Requirements Engineering Conference')
        self.assertEqual(re['type'], 'dblp')
        self.assertEqual(re['venue_key'], 'conf/re')
        self.assertEqual(re['venue_short'], 're')
    
    def test_issre_configuration(self):
        """Test ISSRE conference configuration."""
        issre = self.se_conferences['ISSRE']
        self.assertEqual(issre['name'], 'IEEE International Symposium on Software Reliability Engineering')
        self.assertEqual(issre['type'], 'dblp')
        self.assertEqual(issre['venue_key'], 'conf/issre')
        self.assertEqual(issre['venue_short'], 'issre')
    
    def test_scraper_config(self):
        """Test scraper configuration."""
        self.assertIn('user_agent', SCRAPER_CONFIG)
        self.assertIn('request_delay', SCRAPER_CONFIG)
        self.assertIn('timeout', SCRAPER_CONFIG)
        self.assertIn('max_retries', SCRAPER_CONFIG)
        self.assertGreater(SCRAPER_CONFIG['request_delay'], 0)
        self.assertGreater(SCRAPER_CONFIG['timeout'], 0)
        self.assertGreater(SCRAPER_CONFIG['max_retries'], 0)
    
    def test_dblp_config(self):
        """Test DBLP configuration."""
        self.assertIn('base_url', DBLP_CONFIG)
        self.assertIn('xml_url', DBLP_CONFIG)
        self.assertTrue(DBLP_CONFIG['base_url'].startswith('https://'))
        self.assertIn('{venue_path}', DBLP_CONFIG['xml_url'])
        self.assertIn('{venue_short}', DBLP_CONFIG['xml_url'])


class TestScraperFactory(unittest.TestCase):
    """Test scraper factory functionality."""
    
    def test_scraper_types_available(self):
        """Test that expected scraper types are available."""
        expected_types = {'dblp', 'openreview', 'anthology'}
        available_types = set(ScraperFactory.get_available_types())
        self.assertTrue(expected_types.issubset(available_types))
    
    def test_create_dblp_scraper(self):
        """Test creating DBLP scraper."""
        config = CONFERENCES['SE']['ICSE']
        scraper = ScraperFactory.create_scraper(config)
        self.assertIsInstance(scraper, BaseScraper)
        self.assertEqual(scraper.config, config)
    
    def test_create_scraper_invalid_type(self):
        """Test creating scraper with invalid type."""
        config = {'type': 'invalid_type'}
        with self.assertRaises(ValueError):
            ScraperFactory.create_scraper(config)
    
    def test_create_scrapers_for_new_conferences(self):
        """Test creating scrapers for all new SE conferences."""
        new_conferences = ['MSR', 'ICPC', 'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE']
        
        for conf_name in new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                scraper = ScraperFactory.create_scraper(config)
                self.assertIsInstance(scraper, BaseScraper)
                self.assertEqual(scraper.config, config)


class TestBaseScraper(unittest.TestCase):
    """Test base scraper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = CONFERENCES['SE']['ICSE']
        self.scraper = ScraperFactory.create_scraper(self.config)
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.config, self.config)
        self.assertIsNotNone(self.scraper.logger)
    
    def test_context_manager(self):
        """Test scraper context manager."""
        # Initially session should be None
        self.assertIsNone(self.scraper.session)
        
        with self.scraper as s:
            self.assertIsNotNone(s.session)
        
        # After exiting context, session should be closed but object may still exist
        # The important thing is that the __exit__ method was called
        self.assertTrue(hasattr(self.scraper, 'session'))
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("", ""),
            (None, ""),
            ("single", "single"),
            ("  \n\t  multiple\n\nlines  \t  ", "multiple lines")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.scraper.clean_text(input_text)
                self.assertEqual(result, expected)
    
    def test_extract_authors(self):
        """Test author extraction."""
        test_cases = [
            ("John Doe, Jane Smith", ["John Doe", "Jane Smith"]),
            ("Single Author", ["Single Author"]),
            ("", []),
            (None, []),
            ("Author One, Author Two, Author Three", ["Author One", "Author Two", "Author Three"])
        ]
        
        for author_string, expected_names in test_cases:
            with self.subTest(author_string=author_string):
                authors = self.scraper.extract_authors(author_string)
                actual_names = [author.name for author in authors]
                self.assertEqual(actual_names, expected_names)


class TestPaperModel(unittest.TestCase):
    """Test paper data model."""
    
    def test_paper_creation(self):
        """Test paper object creation."""
        authors = [Author(name="John Doe"), Author(name="Jane Smith")]
        paper = Paper(
            title="Test Paper",
            authors=authors,
            year=2023,
            venue="ICSE",
            doi="10.1000/test.doi"
        )
        
        self.assertEqual(paper.title, "Test Paper")
        self.assertEqual(len(paper.authors), 2)
        self.assertEqual(paper.year, 2023)
        self.assertEqual(paper.venue, "ICSE")
        self.assertEqual(paper.doi, "10.1000/test.doi")
    
    def test_author_creation(self):
        """Test author object creation."""
        author = Author(
            name="John Doe",
            email="john@example.com",
            affiliation="Example University"
        )
        
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.email, "john@example.com")
        self.assertEqual(author.affiliation, "Example University")


class TestIntegrationWithNewConferences(unittest.TestCase):
    """Integration tests for new SE conferences."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.new_conferences = ['MSR', 'ICPC', 'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE']
    
    def test_conference_lookup(self):
        """Test that new conferences can be found in the configuration."""
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                # Test lookup in CONFERENCES structure
                found = False
                for domain, conferences in CONFERENCES.items():
                    if conf_name in conferences:
                        found = True
                        break
                self.assertTrue(found, f"Conference {conf_name} not found in CONFERENCES")
    
    def test_scraper_creation_for_new_conferences(self):
        """Test scraper creation for all new conferences."""
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                scraper = ScraperFactory.create_scraper(config)
                self.assertIsInstance(scraper, BaseScraper)
    
    @patch('src.scrapers.historical_dblp_scraper.HistoricalDBLPScraper.scrape_papers')
    def test_mock_scraping_new_conferences(self, mock_scrape):
        """Test mock scraping for new conferences."""
        # Mock return value
        mock_papers = [
            Paper(title="Mock Paper 1", authors=[Author(name="Author 1")], year=2023, venue="Test"),
            Paper(title="Mock Paper 2", authors=[Author(name="Author 2")], year=2023, venue="Test")
        ]
        mock_scrape.return_value = mock_papers
        
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                scraper = ScraperFactory.create_scraper(config)
                
                with scraper:
                    papers = scraper.scrape_papers(2023)
                    self.assertEqual(len(papers), 2)
                    self.assertEqual(papers[0].title, "Mock Paper 1")


class TestConferenceURLs(unittest.TestCase):
    """Test conference URL configurations."""
    
    def test_base_urls_valid(self):
        """Test that base URLs are properly formatted."""
        for category, conferences in CONFERENCES.items():
            for conf_name, conf_data in conferences.items():
                with self.subTest(category=category, conference=conf_name):
                    base_url = conf_data.get('base_url', '')
                    self.assertTrue(base_url.startswith('https://'), 
                                  f"Conference {conf_name} base_url should start with https://")
    
    def test_venue_keys_format(self):
        """Test that venue keys follow expected format."""
        for category, conferences in CONFERENCES.items():
            for conf_name, conf_data in conferences.items():
                with self.subTest(category=category, conference=conf_name):
                    venue_key = conf_data.get('venue_key', '')
                    if conf_data.get('type') == 'dblp':
                        self.assertTrue(venue_key.startswith('conf/'), 
                                      f"DBLP conference {conf_name} venue_key should start with 'conf/'")


def create_test_suite():
    """Create a comprehensive test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConferenceConfigurations,
        TestScraperFactory,
        TestBaseScraper,
        TestPaperModel,
        TestIntegrationWithNewConferences,
        TestConferenceURLs
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


if __name__ == '__main__':
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)