import sys
import unittest

# Add current directory to path
sys.path.insert(0, '.')

# Import test module
import test_agi

# Create test suite
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(test_agi)

# Run tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Print summary
print(f"\n=== SUMMARY ===")
print(f"Tests run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
print(f"Was successful: {result.wasSuccessful()}")

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)
