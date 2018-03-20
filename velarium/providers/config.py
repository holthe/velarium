from ConfigParser import SafeConfigParser

import pkg_resources

import simpleprovider


class Configuration(object):

    providers = []

    def __init__(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str  # make option names case sensitive
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')

        for item in parser.items('providers'):
            self.providers.append(simpleprovider.SimpleProvider('/home/holthe/.config/velarium', item[0], item[1]))


config = Configuration(pkg_resources.resource_filename('velarium', 'providers.conf'))
