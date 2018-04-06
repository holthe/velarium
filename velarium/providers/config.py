import velarium.utils
try:
    from ConfigParser import SafeConfigParser, NoSectionError
except ImportError:
    from configparser import ConfigParser as SafeConfigParser, NoSectionError

import os
import pkg_resources

from . import simpleprovider


class Configuration(object):

    providers = []

    def __init__(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str  # Make option names case sensitive
        found = parser.read([f for f in file_names if os.path.isfile(f)])
        if not found:
            raise ValueError('No config file found!')

        try:
            for item in parser.items('providers'):
                self.providers.append(simpleprovider.SimpleProvider(velarium.utils.get_app_dir(), item[0], item[1]))
        except NoSectionError:
            pass


# Look for both bundled provider configuration file and a user provided one
config_filename = 'providers.conf'
config = Configuration(pkg_resources.resource_filename('velarium', config_filename),
                       os.path.join(velarium.utils.get_app_dir(), config_filename))
