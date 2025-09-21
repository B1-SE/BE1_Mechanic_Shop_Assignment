#!/usr/bin/env python3
"""
Simple test runner that supports both pytest and unittest discovery.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    # Check if we should run with unittest discovery
    if len(sys.argv) > 1 and 'discover' in sys.argv:
        # Run with unittest discovery as specified in documentation
        import unittest
        
        # Remove 'discover' from argv to prevent issues
        sys.argv.remove('discover')
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = 'tests'
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Exit with error code if tests failed
        sys.exit(not result.wasSuccessful())
    else:
        # Run with pytest (default)
        try:
            import pytest
            sys.exit(pytest.main(['-v'] + sys.argv[1:]))
        except ImportError:
            print("pytest not found, falling back to unittest")
            import unittest
            
            loader = unittest.TestLoader()
            start_dir = 'tests'
            suite = loader.discover(start_dir, pattern='test_*.py')
            
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            sys.exit(not result.wasSuccessful())