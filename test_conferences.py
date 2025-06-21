#!/usr/bin/env python3
"""
Comprehensive test suite for all conference configurations.
Tests multiple years for each conference to ensure robustness.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Test configuration: conference -> [years to test]
TEST_CONFIGS = {
    # Software Engineering
    'SE': {
        'ICSE': [2023, 2022, 2021],
        'FSE': [2023, 2022, 2021], 
        'ASE': [2023, 2022, 2021],
        'ISSTA': [2023, 2022, 2021],
        'ICSA': [2024, 2023, 2022],
        'MSR': [2023, 2022, 2021],
        'ICPC': [2023, 2022, 2021],
        'ICSME': [2023, 2022, 2021],
        'SANER': [2023, 2022, 2021],
        'ECSA': [2023, 2022, 2021],
        'OOPSLA': [2023, 2022, 2021],
        'RE': [2023, 2022, 2021],
        'ISSRE': [2023, 2022, 2021]
    },
    # AI/ML
    'AI_ML': {
        'ICML': [2023, 2022, 2021],
        'NIPS': [2024, 2023, 2022],
        'ICLR': [2023, 2022, 2021],
        'AAAI': [2023, 2022, 2021],
        'IJCAI': [2023, 2022, 2021]
    },
    # NLP
    'NLP': {
        'ACL': [2023, 2022, 2021],
        'EMNLP': [2023, 2022, 2021],
        'NAACL': [2022, 2021, 2019],  # NAACL doesn't happen every year
        'COLING': [2022, 2020]  # COLING is every 2 years
    }
}

# Expected minimum paper counts (to catch major issues)
MIN_PAPERS = {
    'ICSE': 50, 'FSE': 50, 'ASE': 50, 'ISSTA': 20, 'ICSA': 10,
    'MSR': 20, 'ICPC': 15, 'ICSME': 30, 'SANER': 20, 'ECSA': 10,
    'OOPSLA': 30, 'RE': 20, 'ISSRE': 15,
    'ICML': 500, 'NIPS': 1000, 'ICLR': 500, 'AAAI': 500, 'IJCAI': 200,
    'ACL': 300, 'EMNLP': 300, 'NAACL': 100, 'COLING': 200
}

def run_scraper(conference: str, year: int, timeout: int = 60) -> Tuple[bool, str, Dict]:
    """Run the scraper for a conference and year."""
    cmd = ['python', 'main.py', '--scrape', conference, '--year', str(year)]
    
    try:
        print(f"  Testing {conference} {year}... ", end='', flush=True)
        start_time = time.time()
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd='/home/yu/project/PaperHelper'
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # Try to load and analyze the output file
            output_file = Path(f'/home/yu/project/PaperHelper/output/{conference}_{year}.json')
            if output_file.exists():
                with open(output_file) as f:
                    data = json.load(f)
                    paper_count = data.get('total_papers', 0)
                    min_expected = MIN_PAPERS.get(conference, 10)
                    
                    if paper_count >= min_expected:
                        print(f"✅ {paper_count} papers ({elapsed:.1f}s)")
                        return True, f"Success: {paper_count} papers", {
                            'papers': paper_count, 
                            'time': elapsed,
                            'status': 'success'
                        }
                    else:
                        print(f"⚠️  {paper_count} papers (expected ≥{min_expected}) ({elapsed:.1f}s)")
                        return False, f"Too few papers: {paper_count} < {min_expected}", {
                            'papers': paper_count,
                            'time': elapsed, 
                            'status': 'too_few_papers'
                        }
            else:
                print(f"❌ No output file ({elapsed:.1f}s)")
                return False, "No output file created", {'time': elapsed, 'status': 'no_output'}
        else:
            print(f"❌ Exit code {result.returncode} ({elapsed:.1f}s)")
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, f"Command failed: {error_msg}", {
                'time': elapsed,
                'status': 'command_failed',
                'error': error_msg
            }
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after {timeout}s")
        return False, f"Timeout after {timeout}s", {'time': timeout, 'status': 'timeout'}
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, f"Exception: {e}", {'status': 'exception', 'error': str(e)}

def test_all_conferences():
    """Test all conferences and generate a comprehensive report."""
    print("🧪 Starting comprehensive conference testing...")
    print("=" * 80)
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    for category, conferences in TEST_CONFIGS.items():
        print(f"\n📂 {category} Conferences:")
        print("-" * 40)
        
        category_results = {}
        
        for conference, years in conferences.items():
            print(f"\n🏛️  {conference}:")
            conference_results = {}
            
            for year in years:
                total_tests += 1
                success, message, details = run_scraper(conference, year)
                conference_results[year] = {
                    'success': success,
                    'message': message,
                    'details': details
                }
                if success:
                    passed_tests += 1
            
            category_results[conference] = conference_results
        
        results[category] = category_results
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Detailed failure report
    print("\n📋 DETAILED RESULTS:")
    print("-" * 40)
    
    for category, conferences in results.items():
        print(f"\n{category}:")
        for conference, years in conferences.items():
            success_count = sum(1 for year_data in years.values() if year_data['success'])
            total_count = len(years)
            status = "✅" if success_count == total_count else "⚠️" if success_count > 0 else "❌"
            print(f"  {status} {conference}: {success_count}/{total_count}")
            
            # Show failures
            for year, year_data in years.items():
                if not year_data['success']:
                    print(f"    ❌ {year}: {year_data['message']}")
    
    # Performance analysis
    print("\n⏱️  PERFORMANCE ANALYSIS:")
    print("-" * 40)
    
    all_times = []
    for category, conferences in results.items():
        for conference, years in conferences.items():
            for year, year_data in years.items():
                if 'time' in year_data['details']:
                    all_times.append(year_data['details']['time'])
    
    if all_times:
        avg_time = sum(all_times) / len(all_times)
        max_time = max(all_times)
        min_time = min(all_times)
        print(f"Average scraping time: {avg_time:.1f}s")
        print(f"Fastest: {min_time:.1f}s")
        print(f"Slowest: {max_time:.1f}s")
    
    # Save detailed results
    results_file = Path('/home/yu/project/PaperHelper/test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return passed_tests == total_tests

def test_specific_conference(conference: str, year: int):
    """Test a specific conference and year."""
    print(f"🧪 Testing {conference} {year}...")
    success, message, details = run_scraper(conference, year, timeout=120)
    
    if success:
        print(f"✅ Test passed: {message}")
    else:
        print(f"❌ Test failed: {message}")
    
    return success

def main():
    """Main entry point."""
    if len(sys.argv) == 3:
        # Test specific conference and year
        conference = sys.argv[1]
        year = int(sys.argv[2])
        success = test_specific_conference(conference, year)
        sys.exit(0 if success else 1)
    else:
        # Test all conferences
        success = test_all_conferences()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()