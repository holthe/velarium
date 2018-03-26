import unittest

from mock import patch

import velarium.utils


class UtilsTestSuite(unittest.TestCase):
    """Unit and integration test cases for utils."""

    def test_get_resource_ascii_logo(self):
        """Test resource retrieval of ascii_logo."""
        with velarium.utils.get_resource('ascii_logo') as ascii_logo:
            data = ascii_logo.read()
        self.assertTrue(len(data) > 0, 'Failed to load resource ascii_logo.')

    def test_query_yes_no(self):
        """Test answering '' to a yes/no query."""
        self._test_query_yes_no('', True)

    def test_query_yes_no_y(self):
        """Test answering 'y' to a yes/no query."""
        self._test_query_yes_no('y', True)

    def test_query_yes_no_ye(self):
        """Test answering 'ye' to a yes/no query."""
        self._test_query_yes_no('ye', True)

    def test_query_yes_no_yes(self):
        """Test answering 'yes' to a yes/no query."""
        self._test_query_yes_no('yes', True)

    def test_query_yes_no_n(self):
        """Test answering 'n' to a yes/no query."""
        self._test_query_yes_no('n', False)

    def test_query_yes_no_no(self):
        """Test answering 'no' to a yes/no query."""
        self._test_query_yes_no('no', False)

    def _test_query_yes_no(self, input_value, expected_output):
        input_to_patch = 'velarium.utils.input'

        with patch(input_to_patch, return_value=input_value) as _input:
            self.assertEqual(velarium.utils.query_yes_no('Are you OK?'), expected_output)
            _input.assert_called_once_with()
