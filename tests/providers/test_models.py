import unittest

import velarium.providers.models


class ModelsTestSuite(unittest.TestCase):
    """Unit tests for models."""

    server_title = 'title'
    server_hostname = 'hostname'

    def test_can_construct_server(self):
        """Test construction of a server."""
        server = velarium.providers.models.Server(self.server_title, self.server_hostname, self.server_hostname)

        self.assertIsNotNone(server)
        self.assertEqual(server.title, self.server_title)
        self.assertEqual(server.hostname, self.server_hostname)
        self.assertEqual(server.config_selector, self.server_hostname)
        self.assertEqual(server.rtt, -1)

    def test_can_set_rtt(self):
        """Test setting rtt on a constructed server."""
        rtt = 50

        server = velarium.providers.models.Server(self.server_title, self.server_hostname, self.server_hostname)
        server.set_rtt(50)
        self.assertEqual(server.rtt, rtt)

    def test_server_str_contains_title(self):
        """Test server string representation."""
        server = velarium.providers.models.Server(self.server_title, self.server_hostname, self.server_hostname)

        self.assertTrue(str(server).startswith(self.server_title))
