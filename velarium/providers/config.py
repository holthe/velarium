import velarium.utils
try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import ConfigParser as SafeConfigParser

import pkg_resources

from . import simpleprovider


class Configuration(object):

    providers = []

    def __init__(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str  # Make option names case sensitive
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')

        for item in parser.items('providers'):
            self.providers.append(simpleprovider.SimpleProvider(velarium.utils.get_app_dir(), item[0], item[1]))


config = Configuration(pkg_resources.resource_filename('velarium', 'providers.conf'))
