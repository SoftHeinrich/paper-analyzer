#!/usr/bin/env python3
"""
Test runner for PaperHelper unit tests.
Runs all unit tests and provides comprehensive reporting.
"""

import unittest
import sys
import os
from pathlib import Path
import time

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    print("🧪 PaperHelper Unit Test Suite")
    print("=" * 50)
    
    # Discover tests
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent / 'tests'
    
    if not test_dir.exists():
        print("❌ Tests directory not found!")
        return False
    
    suite = loader.discover(str(test_dir), pattern='test*.py')
    
    # Count total tests
    def count_tests(test_suite):
        count = 0
        for test in test_suite:
            if hasattr(test, '__iter__'):
                count += count_tests(test)
            else:
                count += 1
        return count
    
    total_tests = count_tests(suite)
    print(f"Found {total_tests} tests")
    print()
    
    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"Execution time: {end_time - start_time:.2f}s")
    
    # Print failures and errors if any
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        print("-" * 30)
        for test, traceback in result.failures:
            print(f"• {test}")
            print(f"  {traceback.split('AssertionError:')[-1].split('\\n')[0].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        print("-" * 30)
        for test, traceback in result.errors:
            print(f"• {test}")
            print(f"  {traceback.split('Exception:')[-1].split('\\n')[0].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} test(s) failed")
    
    return result.wasSuccessful()


def run_specific_test_file(test_file):
    """Run tests from a specific file."""
    print(f"🧪 Running tests from {test_file}")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    
    try:
        # Import the test module
        test_module_name = f"tests.{test_file.replace('.py', '')}"
        suite = loader.loadTestsFromName(test_module_name)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Error loading test file {test_file}: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        if not test_file.endswith('.py'):
            test_file += '.py'
        
        success = run_specific_test_file(test_file)
    else:
        # Run all tests
        success = discover_and_run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()