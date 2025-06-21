#!/usr/bin/env python3
"""
Quick test of key conferences to identify any major issues.
"""

import subprocess
import sys
import json
from pathlib import Path
import time

# Quick test configuration: one recent year for each major conference
QUICK_TESTS = [
    ('ICSE', 2023),
    ('FSE', 2023), 
    ('ICSA', 2024),
    ('ICML', 2023),
    ('NIPS', 2024),
    ('ICLR', 2023),
    ('AAAI', 2023),
    ('ACL', 2023),
    ('EMNLP', 2023)
]

def run_quick_test():
    """Run quick tests on key conferences."""
    print("🧪 Running quick conference tests...")
    print("=" * 60)
    
    results = []
    total_papers = 0
    
    for conference, year in QUICK_TESTS:
        print(f"Testing {conference} {year}... ", end='', flush=True)
        
        cmd = ['python', 'main.py', '--scrape', conference, '--year', str(year)]
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                cwd='/home/yu/project/PaperHelper'
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Check output file
                output_file = Path(f'/home/yu/project/PaperHelper/output/{conference}_{year}.json')
                if output_file.exists():
                    with open(output_file) as f:
                        data = json.load(f)
                        papers = data.get('total_papers', 0)
                        total_papers += papers
                        
                        print(f"✅ {papers} papers ({elapsed:.1f}s)")
                        results.append((conference, year, True, papers, elapsed))
                else:
                    print(f"❌ No output")
                    results.append((conference, year, False, 0, elapsed))
            else:
                print(f"❌ Failed")
                results.append((conference, year, False, 0, elapsed))
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout")
            results.append((conference, year, False, 0, 60))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((conference, year, False, 0, 0))
    
    # Summary
    passed = sum(1 for r in results if r[2])
    total = len(results)
    avg_time = sum(r[4] for r in results) / total if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total} ({(passed/total)*100:.0f}%)")
    print(f"Total papers scraped: {total_papers:,}")
    print(f"Average time per conference: {avg_time:.1f}s")
    
    if passed < total:
        print("\n❌ FAILURES:")
        for conf, year, success, papers, elapsed in results:
            if not success:
                print(f"  {conf} {year}")
    
    return passed == total

if __name__ == '__main__':
    success = run_quick_test()
    sys.exit(0 if success else 1)