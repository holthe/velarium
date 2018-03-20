import unittest

import velarium.network


class NetworkTestSuite(unittest.TestCase):
    """Unit and integration test cases for network."""

    def test_download(self):
        """Test downloading ca.ipvanish.com.crt from ipvanish.com."""
        url = 'https://www.ipvanish.com/software/configs/ca.ipvanish.com.crt'
        with velarium.network.download(url, chunk=False, verbose=False) as d:
            data = d.getvalue()
        self.assertTrue(len(data) > 0)

    def test_get_dns_info(self):
        """Test retrieval of DNS info."""
        self.assertTrue(len(velarium.network.get_dns_info()) > 0, 'Failed to retrieve DNS info.')
