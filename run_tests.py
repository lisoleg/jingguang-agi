import unittest
import sys
from io import StringIO

# Capture stdout and stderr
sys.stdout = StringIO()
sys.stderr = StringIO()

# Run tests
loader = unittest.TestLoader()
suite = loader.loadTestsFromName('test_agi')
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Restore stdout and print captured output
stdout = sys.stdout.getvalue()
stderr = sys.stderr.getvalue()
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

print("=== STDOUT ===")
print(stdout)
print("=== STDERR ===")
print(stderr)
print("=== RESULT ===")
print(f"Tests run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
if result.failures:
    print("Failures:")
    for test, traceback in result.failures:
        print(test)
        print(traceback)
if result.errors:
    print("Errors:")
    for test, traceback in result.errors:
        print(test)
        print(traceback)
