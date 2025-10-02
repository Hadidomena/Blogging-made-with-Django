#!/usr/bin/env python
"""API Test Runner - Usage: python test_api_runner.py [-v] [--coverage]"""
import os
import sys
import subprocess

def run_api_tests(verbose=False, coverage=False):
    # Ensure we're in the Django project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Base command
    cmd = [sys.executable, 'manage.py', 'test', 'webBlog.test_api']
    
    # Add verbose flag if requested
    if verbose:
        cmd.extend(['-v', '2'])
    
    # Run with coverage if requested
    if coverage:
        try:
            import coverage as cov
            cmd = ['coverage', 'run', '--source=.', 'manage.py', 'test', 'webBlog.test_api']
            if verbose:
                cmd.extend(['-v', '2'])
        except ImportError:
            print("Coverage not installed. Install with: pip install coverage")
            return False
    
    print("Running API tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd)
    
    # Show coverage report if requested
    if coverage and result.returncode == 0:
        print("\nGenerating coverage report...")
        subprocess.run(['coverage', 'report'])
        print("\nTo see detailed HTML coverage report, run: coverage html")
    
    return result.returncode == 0

if __name__ == '__main__':
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    coverage = '--coverage' in sys.argv
    
    success = run_api_tests(verbose=verbose, coverage=coverage)
    
    if success:
        print("\n✅ All API tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)