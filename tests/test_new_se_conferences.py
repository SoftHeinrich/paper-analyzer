#!/usr/bin/env python3
"""
Specialized unit tests for the newly added SE conferences.
Tests specific configurations and expected behaviors for MSR, ICPC, ICSME, SANER, ECSA, OOPSLA, RE, ISSRE.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.conferences import CONFERENCES
from src.scrapers import ScraperFactory
from src.models.paper import Paper, Author


class TestMSRConference(unittest.TestCase):
    """Test MSR (Mining Software Repositories) conference configuration."""
    
    def setUp(self):
        self.msr_config = CONFERENCES['SE']['MSR']
    
    def test_msr_basic_config(self):
        """Test MSR basic configuration."""
        self.assertEqual(self.msr_config['name'], 'International Conference on Mining Software Repositories')
        self.assertEqual(self.msr_config['venue_short'], 'msr')
        self.assertEqual(self.msr_config['type'], 'dblp')
        self.assertTrue(self.msr_config['base_url'].startswith('https://'))
    
    def test_msr_dblp_config(self):
        """Test MSR DBLP-specific configuration."""
        self.assertEqual(self.msr_config['venue_key'], 'conf/msr')
        self.assertEqual(self.msr_config['venue_path'], 'conf/msr')
    
    def test_msr_scraper_creation(self):
        """Test creating scraper for MSR."""
        scraper = ScraperFactory.create_scraper(self.msr_config)
        self.assertIsNotNone(scraper)
        self.assertEqual(scraper.config, self.msr_config)


class TestICPCConference(unittest.TestCase):
    """Test ICPC (Program Comprehension) conference configuration."""
    
    def setUp(self):
        self.icpc_config = CONFERENCES['SE']['ICPC']
    
    def test_icpc_basic_config(self):
        """Test ICPC basic configuration."""
        self.assertEqual(self.icpc_config['name'], 'IEEE International Conference on Program Comprehension')
        self.assertEqual(self.icpc_config['venue_short'], 'icpc')
        self.assertEqual(self.icpc_config['type'], 'dblp')
    
    def test_icpc_venue_mapping(self):
        """Test ICPC venue mapping to DBLP (IWPC)."""
        # ICPC maps to IWPC in DBLP
        self.assertEqual(self.icpc_config['venue_key'], 'conf/iwpc')
        self.assertEqual(self.icpc_config['venue_path'], 'conf/iwpc')
    
    def test_icpc_scraper_creation(self):
        """Test creating scraper for ICPC."""
        scraper = ScraperFactory.create_scraper(self.icpc_config)
        self.assertIsNotNone(scraper)


class TestICSMEConference(unittest.TestCase):
    """Test ICSME (Software Maintenance and Evolution) conference configuration."""
    
    def setUp(self):
        self.icsme_config = CONFERENCES['SE']['ICSME']
    
    def test_icsme_basic_config(self):
        """Test ICSME basic configuration."""
        self.assertEqual(self.icsme_config['name'], 'IEEE International Conference on Software Maintenance and Evolution')
        self.assertEqual(self.icsme_config['venue_short'], 'icsme')
    
    def test_icsme_venue_mapping(self):
        """Test ICSME venue mapping to DBLP (ICSM)."""
        # ICSME maps to ICSM in DBLP
        self.assertEqual(self.icsme_config['venue_key'], 'conf/icsm')
        self.assertEqual(self.icsme_config['venue_path'], 'conf/icsm')


class TestSANERConference(unittest.TestCase):
    """Test SANER (Software Analysis, Evolution and Reengineering) conference configuration."""
    
    def setUp(self):
        self.saner_config = CONFERENCES['SE']['SANER']
    
    def test_saner_basic_config(self):
        """Test SANER basic configuration."""
        self.assertEqual(self.saner_config['name'], 'IEEE International Conference on Software Analysis, Evolution and Reengineering')
        self.assertEqual(self.saner_config['venue_short'], 'saner')
    
    def test_saner_venue_mapping(self):
        """Test SANER venue mapping to DBLP (WCRE)."""
        # SANER evolved from WCRE in DBLP
        self.assertEqual(self.saner_config['venue_key'], 'conf/wcre')
        self.assertEqual(self.saner_config['venue_path'], 'conf/wcre')


class TestECSAConference(unittest.TestCase):
    """Test ECSA (European Conference on Software Architecture) conference configuration."""
    
    def setUp(self):
        self.ecsa_config = CONFERENCES['SE']['ECSA']
    
    def test_ecsa_basic_config(self):
        """Test ECSA basic configuration."""
        self.assertEqual(self.ecsa_config['name'], 'European Conference on Software Architecture')
        self.assertEqual(self.ecsa_config['venue_short'], 'ecsa')
    
    def test_ecsa_dblp_config(self):
        """Test ECSA DBLP configuration."""
        self.assertEqual(self.ecsa_config['venue_key'], 'conf/ecsa')
        self.assertEqual(self.ecsa_config['venue_path'], 'conf/ecsa')


class TestOOPSLAConference(unittest.TestCase):
    """Test OOPSLA (Object-Oriented Programming, Systems, Languages, and Applications) conference configuration."""
    
    def setUp(self):
        self.oopsla_config = CONFERENCES['SE']['OOPSLA']
    
    def test_oopsla_basic_config(self):
        """Test OOPSLA basic configuration."""
        expected_name = 'ACM Conference on Object-Oriented Programming, Systems, Languages, and Applications'
        self.assertEqual(self.oopsla_config['name'], expected_name)
        self.assertEqual(self.oopsla_config['venue_short'], 'oopsla')
    
    def test_oopsla_dblp_config(self):
        """Test OOPSLA DBLP configuration."""
        self.assertEqual(self.oopsla_config['venue_key'], 'conf/oopsla')
        self.assertEqual(self.oopsla_config['venue_path'], 'conf/oopsla')
    
    def test_oopsla_base_url(self):
        """Test OOPSLA base URL points to SPLASH."""
        # OOPSLA is part of SPLASH conference
        self.assertIn('splash', self.oopsla_config['base_url'].lower())


class TestREConference(unittest.TestCase):
    """Test RE (Requirements Engineering) conference configuration."""
    
    def setUp(self):
        self.re_config = CONFERENCES['SE']['RE']
    
    def test_re_basic_config(self):
        """Test RE basic configuration."""
        self.assertEqual(self.re_config['name'], 'IEEE International Requirements Engineering Conference')
        self.assertEqual(self.re_config['venue_short'], 're')
    
    def test_re_dblp_config(self):
        """Test RE DBLP configuration."""
        self.assertEqual(self.re_config['venue_key'], 'conf/re')
        self.assertEqual(self.re_config['venue_path'], 'conf/re')


class TestISSREConference(unittest.TestCase):
    """Test ISSRE (Software Reliability Engineering) conference configuration."""
    
    def setUp(self):
        self.issre_config = CONFERENCES['SE']['ISSRE']
    
    def test_issre_basic_config(self):
        """Test ISSRE basic configuration."""
        self.assertEqual(self.issre_config['name'], 'IEEE International Symposium on Software Reliability Engineering')
        self.assertEqual(self.issre_config['venue_short'], 'issre')
    
    def test_issre_dblp_config(self):
        """Test ISSRE DBLP configuration."""
        self.assertEqual(self.issre_config['venue_key'], 'conf/issre')
        self.assertEqual(self.issre_config['venue_path'], 'conf/issre')


class TestNewConferencesIntegration(unittest.TestCase):
    """Integration tests for all new SE conferences."""
    
    def setUp(self):
        self.new_conferences = ['MSR', 'ICPC', 'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE']
    
    def test_all_new_conferences_in_se_category(self):
        """Test that all new conferences are in the SE category."""
        se_conferences = set(CONFERENCES['SE'].keys())
        for conf in self.new_conferences:
            self.assertIn(conf, se_conferences, f"Conference {conf} not found in SE category")
    
    def test_all_new_conferences_have_dblp_type(self):
        """Test that all new conferences use DBLP scraper type."""
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                self.assertEqual(config['type'], 'dblp', f"{conf_name} should use DBLP scraper")
    
    def test_venue_keys_are_unique(self):
        """Test that venue keys are unique across all SE conferences."""
        venue_keys = []
        for conf_name, config in CONFERENCES['SE'].items():
            venue_keys.append(config['venue_key'])
        
        # Check for duplicates
        duplicates = [key for key in set(venue_keys) if venue_keys.count(key) > 1]
        self.assertEqual(len(duplicates), 0, f"Duplicate venue keys found: {duplicates}")
    
    def test_venue_shorts_are_unique(self):
        """Test that venue short names are unique across all SE conferences."""
        venue_shorts = []
        for conf_name, config in CONFERENCES['SE'].items():
            venue_shorts.append(config['venue_short'])
        
        # Check for duplicates
        duplicates = [short for short in set(venue_shorts) if venue_shorts.count(short) > 1]
        self.assertEqual(len(duplicates), 0, f"Duplicate venue shorts found: {duplicates}")
    
    @patch('src.scrapers.historical_dblp_scraper.HistoricalDBLPScraper.scrape_papers')
    def test_mock_scraping_all_new_conferences(self, mock_scrape):
        """Test mock scraping for all new conferences."""
        # Mock successful scraping
        mock_papers = [
            Paper(title=f"Test Paper 1", authors=[Author(name="Author 1")], year=2023, venue="Test"),
            Paper(title=f"Test Paper 2", authors=[Author(name="Author 2")], year=2023, venue="Test")
        ]
        mock_scrape.return_value = mock_papers
        
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                scraper = ScraperFactory.create_scraper(config)
                
                with scraper:
                    papers = scraper.scrape_papers(2023)
                    self.assertIsInstance(papers, list)
                    self.assertGreater(len(papers), 0)
    
    def test_conference_names_are_descriptive(self):
        """Test that conference names are properly descriptive."""
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                name = config['name']
                
                # Should contain conference-related keywords
                self.assertTrue(
                    'Conference' in name or 'Symposium' in name,
                    f"{conf_name} name should contain 'Conference' or 'Symposium'"
                )
                
                # Should be reasonably long (not just abbreviation)
                self.assertGreater(len(name), 20, f"{conf_name} name seems too short")
    
    def test_base_urls_accessible_format(self):
        """Test that base URLs follow expected format."""
        for conf_name in self.new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                base_url = config['base_url']
                
                # Should be HTTPS
                self.assertTrue(base_url.startswith('https://'), 
                              f"{conf_name} base_url should use HTTPS")
                
                # Should be a valid URL format
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                self.assertTrue(parsed.netloc, f"{conf_name} base_url should have a domain")


class TestConferenceMetadata(unittest.TestCase):
    """Test metadata consistency for new conferences."""
    
    def test_venue_key_path_consistency(self):
        """Test that venue_key and venue_path are consistent."""
        new_conferences = ['MSR', 'ICPC', 'ICSME', 'SANER', 'ECSA', 'OOPSLA', 'RE', 'ISSRE']
        
        for conf_name in new_conferences:
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                
                # For most conferences, venue_key and venue_path should be the same
                # except for some special cases like ICPC->IWPC, ICSME->ICSM, SANER->WCRE
                venue_key = config['venue_key']
                venue_path = config['venue_path']
                
                # They should at least have the same structure (conf/something)
                self.assertTrue(venue_key.startswith('conf/'), 
                              f"{conf_name} venue_key should start with 'conf/'")
                self.assertTrue(venue_path.startswith('conf/'), 
                              f"{conf_name} venue_path should start with 'conf/'")
    
    def test_special_venue_mappings(self):
        """Test special venue mappings for conferences that changed names."""
        special_mappings = {
            'ICPC': 'iwpc',    # ICPC maps to IWPC in DBLP
            'ICSME': 'icsm',   # ICSME maps to ICSM in DBLP  
            'SANER': 'wcre'    # SANER evolved from WCRE
        }
        
        for conf_name, expected_dblp_name in special_mappings.items():
            with self.subTest(conference=conf_name):
                config = CONFERENCES['SE'][conf_name]
                self.assertTrue(config['venue_key'].endswith(expected_dblp_name),
                              f"{conf_name} should map to {expected_dblp_name} in DBLP")


if __name__ == '__main__':
    unittest.main(verbosity=2)