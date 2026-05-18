from test_agi import TestTaskInterface
import unittest

suite = unittest.TestLoader().loadTestsFromTestCase(TestTaskInterface)
suite.run(unittest.TestResult())
# Run test_task_summary
test = TestTaskInterface('test_task_summary')
try:
    test.setUp()
    test.test_task_summary()
    print("test_task_summary passed")
except Exception as e:
    print(f"test_task_summary failed: {e}")
    import traceback
    traceback.print_exc()
