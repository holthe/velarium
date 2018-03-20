import itertools
import unittest

import velarium.providers.providers


class ProvidersTestSuite(unittest.TestCase):
    """Unit tests for providers."""

    def test_can_get_ipvanish_provider(self):
        """Test retrieval of IPVanish provider."""
        self._test_all_possible_names('ipvanish')

    def test_can_get_pia_provider(self):
        """Test retrieval of PIA provider."""
        self._test_all_possible_names('pia')

    def test_can_get_all_available_providers(self):
        """Test retrieval of each of the available providers."""
        for name in velarium.providers.providers.available_provider_names:
            provider = self._get_provider(name)
            self.assertIsNotNone(provider, msg=provider.get_name())
            self.assertIsNotNone(provider.configs_url, msg=provider.get_name())

    def _test_all_possible_names(self, base_name):
        for name in self._get_all_possible_names(base_name):
            self.assertIsNotNone(self._get_provider(name))

    @staticmethod
    def _get_all_possible_names(base_name):
        return map(''.join, itertools.product(*((c.upper(), c.lower()) for c in base_name)))

    @staticmethod
    def _get_provider(provider_name):
        return velarium.providers.providers.get_provider(provider_name, '.')
