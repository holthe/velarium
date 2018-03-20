import unittest

import velarium.providers.ipvanish


class IPVanishTestSuite(unittest.TestCase):
    """Unit tests for the IPVanish VPN provider."""

    def test_can_construct(self):
        """Test construction of IPVanish VPN provider."""
        ipvanish = velarium.providers.ipvanish.IPVanish('.')
        self.assertIsNotNone(ipvanish)

        if not ipvanish.cert_file:
            self.fail()

    def test_has_name(self):
        """Test name of IPVanish VPN provider."""
        ipvanish = velarium.providers.ipvanish.IPVanish('.')
        self.assertEqual(ipvanish.get_name(), 'IPVanish')
