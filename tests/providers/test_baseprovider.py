import unittest

import velarium.providers.baseprovider


class BaseProviderTestSuite(unittest.TestCase):
    """Unit tests for the IPVanish VPN provider."""

    def test_construction_raises(self):
        """Test direct construction of base provider not allowed."""
        self.assertRaises(NotImplementedError, velarium.providers.baseprovider.BaseProvider, '.')
