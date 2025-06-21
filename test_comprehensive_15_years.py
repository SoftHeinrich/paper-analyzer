#!/usr/bin/env python3
"""
Comprehensive test script for all conferences across 15 years (2009-2024).
This script performs actual scraping tests to validate historical data availability.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from config.conference_history import (
    get_all_conferences, get_all_test_years, conference_exists_in_year,
    get_expected_min_papers, get_venue_for_year, get_predecessor_conferences
)
from config.conferences import CONFERENCES


@dataclass
class TestResult:
    """Result of testing a conference for a specific year."""
    conference: str
    year: int
    success: bool
    papers_found: int
    expected_min: int
    time_taken: float
    error_message: Optional[str] = None
    venue_used: Optional[str] = None
    

class ComprehensiveHistoricalTester:
    """Comprehensive tester for all conferences across 15 years."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.timeout = 120  # 2 minutes per test
        self.test_years = get_all_test_years()  # 2009-2024
        
    def run_single_test(self, conference: str, year: int) -> TestResult:
        """Run a single test for a conference and year."""
        print(f"  Testing {conference} {year}... ", end='', flush=True)
        start_time = time.time()
        
        # Check if conference should exist in this year
        if not conference_exists_in_year(conference, year):
            elapsed = time.time() - start_time
            print(f"⏭️  N/A (conference didn't exist) ({elapsed:.1f}s)")
            return TestResult(
                conference=conference,
                year=year,
                success=True,  # Not existing is expected
                papers_found=0,
                expected_min=0,
                time_taken=elapsed,
                error_message="Conference didn't exist in this year"
            )
        
        # Get expected minimum papers
        expected_min = get_expected_min_papers(conference, year)
        
        # Get venue information
        try:
            venue_key, venue_short = get_venue_for_year(conference, year)
            venue_used = f"{venue_key}/{venue_short}"
        except ValueError:
            venue_used = "Unknown"
        
        # Run the scraper
        cmd = ['python', 'main.py', '--scrape', conference, '--year', str(year)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(Path(__file__).parent)
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Try to parse the output to get paper count
                papers_found = self._extract_paper_count(result.stdout, conference, year)
                
                if papers_found >= expected_min:
                    print(f"✅ {papers_found} papers ({elapsed:.1f}s)")
                    return TestResult(
                        conference=conference,
                        year=year,
                        success=True,
                        papers_found=papers_found,
                        expected_min=expected_min,
                        time_taken=elapsed,
                        venue_used=venue_used
                    )
                else:
                    print(f"⚠️  {papers_found} papers (expected ≥{expected_min}) ({elapsed:.1f}s)")
                    return TestResult(
                        conference=conference,
                        year=year,
                        success=False,
                        papers_found=papers_found,
                        expected_min=expected_min,
                        time_taken=elapsed,
                        error_message=f"Too few papers: {papers_found} < {expected_min}",
                        venue_used=venue_used
                    )
            else:
                print(f"❌ Exit code {result.returncode} ({elapsed:.1f}s)")
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return TestResult(
                    conference=conference,
                    year=year,
                    success=False,
                    papers_found=0,
                    expected_min=expected_min,
                    time_taken=elapsed,
                    error_message=f"Command failed: {error_msg}",
                    venue_used=venue_used
                )
                
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            print(f"❌ Timeout after {self.timeout}s")
            return TestResult(
                conference=conference,
                year=year,
                success=False,
                papers_found=0,
                expected_min=expected_min,
                time_taken=elapsed,
                error_message=f"Timeout after {self.timeout}s",
                venue_used=venue_used
            )
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Exception: {e} ({elapsed:.1f}s)")
            return TestResult(
                conference=conference,
                year=year,
                success=False,
                papers_found=0,
                expected_min=expected_min,
                time_taken=elapsed,
                error_message=f"Exception: {e}",
                venue_used=venue_used
            )
    
    def _extract_paper_count(self, output: str, conference: str, year: int) -> int:
        """Extract paper count from scraper output."""
        try:
            # Look for "Found X papers" in output
            lines = output.split('\n')
            for line in lines:
                if 'Found' in line and 'papers' in line:
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.isdigit() and i > 0 and words[i-1].lower() == 'found':
                            return int(word)
            
            # Try to parse from JSON file if output parsing fails
            output_file = Path(__file__).parent / f"output/{conference}_{year}.json"
            if output_file.exists():
                with open(output_file) as f:
                    data = json.load(f)
                    return data.get('total_papers', 0)
                    
        except Exception:
            pass
        
        return 0
    
    def test_all_se_conferences(self) -> Dict[str, List[TestResult]]:
        """Test all SE conferences across all years."""
        se_conferences = ['ICSE', 'FSE', 'ASE', 'ISSTA', 'MSR', 'ICPC', 'ICSME', 
                         'SANER', 'ICSA', 'ECSA', 'OOPSLA', 'RE', 'ISSRE']
        
        results = {}
        
        for conference in se_conferences:
            print(f"\n🏛️  Testing {conference}:")
            conference_results = []
            
            for year in self.test_years:
                result = self.run_single_test(conference, year)
                conference_results.append(result)
                self.results.append(result)
            
            results[conference] = conference_results
        
        return results
    
    def test_sample_ai_ml_conferences(self) -> Dict[str, List[TestResult]]:
        """Test sample AI/ML conferences for key years."""
        ai_ml_conferences = ['ICML', 'NIPS', 'ICLR', 'AAAI']
        key_years = [2010, 2015, 2020, 2023]  # Sample years
        
        results = {}
        
        for conference in ai_ml_conferences:
            print(f"\n🤖 Testing {conference} (sample years):")
            conference_results = []
            
            for year in key_years:
                result = self.run_single_test(conference, year)
                conference_results.append(result)
                self.results.append(result)
            
            results[conference] = conference_results
        
        return results
    
    def test_predecessor_conferences(self):
        """Test specific predecessor conference scenarios."""
        print("\n🔄 Testing predecessor conference scenarios:")
        
        # Test SANER predecessors (WCRE, CSMR)
        predecessor_tests = [
            ('SANER', 2012),  # Should use WCRE/CSMR
            ('SANER', 2014),  # Should use WCRE/CSMR  
            ('ICSME', 2011),  # Should use ICSM
            ('ICSME', 2013),  # Should use ICSM
            ('ICSA', 2015),   # Should use WICSA
        ]
        
        for conference, year in predecessor_tests:
            result = self.run_single_test(conference, year)
            self.results.append(result)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        
        # Group results by conference
        by_conference = defaultdict(list)
        for result in self.results:
            by_conference[result.conference].append(result)
        
        # Calculate statistics
        conference_stats = {}
        for conference, results in by_conference.items():
            successful = sum(1 for r in results if r.success)
            total = len(results)
            total_papers = sum(r.papers_found for r in results)
            avg_time = sum(r.time_taken for r in results) / total if total > 0 else 0
            
            conference_stats[conference] = {
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'total_tests': total,
                'successful_tests': successful,
                'total_papers_found': total_papers,
                'average_time': avg_time,
                'failures': [r for r in results if not r.success]
            }
        
        # Year-wise statistics
        by_year = defaultdict(list)
        for result in self.results:
            by_year[result.year].append(result)
        
        year_stats = {}
        for year, results in by_year.items():
            successful = sum(1 for r in results if r.success)
            total = len(results)
            year_stats[year] = {
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'total_tests': total,
                'successful_tests': successful
            }
        
        return {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_time': sum(r.time_taken for r in self.results)
            },
            'by_conference': dict(conference_stats),
            'by_year': dict(year_stats),
            'all_results': [
                {
                    'conference': r.conference,
                    'year': r.year,
                    'success': r.success,
                    'papers_found': r.papers_found,
                    'expected_min': r.expected_min,
                    'time_taken': r.time_taken,
                    'error_message': r.error_message,
                    'venue_used': r.venue_used
                }
                for r in self.results
            ]
        }
    
    def print_summary(self, report: Dict):
        """Print test summary."""
        summary = report['summary']
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE 15-YEAR TESTING SUMMARY")
        print(f"{'='*80}")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['total_tests'] - summary['successful_tests']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total time: {summary['total_time']:.1f}s")
        
        print(f"\n📊 BY CONFERENCE:")
        print("-" * 50)
        for conference, stats in report['by_conference'].items():
            status = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 50 else "❌"
            print(f"{status} {conference:8}: {stats['successful_tests']:2}/{stats['total_tests']:2} "
                  f"({stats['success_rate']:5.1f}%) - {stats['total_papers_found']:4} papers "
                  f"- {stats['average_time']:5.1f}s avg")
        
        print(f"\n📅 BY YEAR:")
        print("-" * 30)
        for year in sorted(report['by_year'].keys()):
            stats = report['by_year'][year]
            status = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 50 else "❌"
            print(f"{status} {year}: {stats['successful_tests']:2}/{stats['total_tests']:2} "
                  f"({stats['success_rate']:5.1f}%)")
        
        # Show failures
        print(f"\n❌ FAILURES:")
        print("-" * 30)
        failure_count = 0
        for conference, stats in report['by_conference'].items():
            for failure in stats['failures']:
                if failure_count < 20:  # Limit output
                    print(f"• {failure.conference} {failure.year}: {failure.error_message}")
                    failure_count += 1
        
        if failure_count == 20:
            total_failures = sum(len(stats['failures']) for stats in report['by_conference'].values())
            print(f"... and {total_failures - 20} more failures")


def main():
    """Main entry point."""
    print("🧪 Comprehensive 15-Year Conference Testing")
    print("Testing all conferences from 2009-2024, including predecessors")
    print(f"{'='*80}")
    
    tester = ComprehensiveHistoricalTester()
    
    # Test SE conferences (most comprehensive)
    se_results = tester.test_all_se_conferences()
    
    # Test sample AI/ML conferences
    ai_ml_results = tester.test_sample_ai_ml_conferences()
    
    # Test predecessor scenarios
    tester.test_predecessor_conferences()
    
    # Generate and save report
    report = tester.generate_report()
    
    # Save detailed results
    results_file = Path(__file__).parent / 'comprehensive_15_year_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Print summary
    tester.print_summary(report)
    
    # Exit with appropriate code
    success_rate = report['summary']['success_rate']
    sys.exit(0 if success_rate >= 75 else 1)  # 75% success rate threshold


if __name__ == '__main__':
    main()