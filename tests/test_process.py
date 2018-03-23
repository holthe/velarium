import unittest

import velarium.process


class ProcessTestSuite(unittest.TestCase):
    """Unit and integration test cases for process."""

    def test_try_call_success(self):
        """Test calling a successful command."""
        self.assertTrue(velarium.process.try_call(['ls'], quiet=True))

    def test_try_call_fail(self):
        """Test calling failing command."""
        self.assertFalse(velarium.process.try_call(['false'], quiet=True))
