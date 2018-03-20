import json
import os

import baseprovider
import models
import velarium.network


class IPVanish(baseprovider.BaseProvider):

    configs_url = 'https://ipvanish.com/software/configs/configs.zip'

    def __init__(self, app_dir):
        super(IPVanish, self).__init__(app_dir)
        self.cert_file = os.path.join(self.config_dir, 'ca.ipvanish.com.crt')

    @staticmethod
    def get_name():
        return 'IPVanish'

    def _get_servers(self):
        """Download and filter IPVanish servers by performing a ping sweep."""
        for _ in xrange(3):
            try:
                with velarium.network.download('https://www.ipvanish.com/api/servers.geojson') as servers_mem_file:
                    data = servers_mem_file.getvalue()

                servers = [IPVanishServer(**server) for server in json.loads(data)]
                sorted_servers = [server for server in sorted(servers)
                                  if server.online and 0 < server.capacity < 40]

                servers_for_ping = []
                for server in sorted_servers:
                    server_for_ping = models.Server(str(server), server.hostname, server.get_config_selector())
                    servers_for_ping.append(server_for_ping)

                return servers_for_ping
            except Exception as err:
                print('[!] Caught exception {0}...'.format(err))

        return []


class IPVanishServer(object):
    """Class representing an IPVanish server."""

    def __init__(self, **entries):
        """Construct a model of an IPVanish server."""
        props = entries['properties']
        self.countryCode = self._get_value(props, 'countryCode')
        self.ip = self._get_value(props, 'ip')
        self.regionAbbr = self._get_value(props, 'regionAbbr')
        self.continent = self._get_value(props, 'continent')
        self.continentCode = self._get_value(props, 'continentCode')
        self.city = self._get_value(props, 'city')
        self.capacity = self._get_value(props, 'capacity')
        self.title = self._get_value(props, 'title')
        self.country = self._get_value(props, 'country')
        self.region = self._get_value(props, 'region')
        self.hostname = self._get_value(props, 'hostname')
        self.longitude = self._get_value(props, 'longitude')
        self.regionCode = self._get_value(props, 'regionCode')
        self.online = self._get_value(props, 'online')
        self.latitude = self._get_value(props, 'latitude')

    def get_config_selector(self):
        """Get the configuration selector, which is used to match a server with a (.ovpn) configuration file."""
        return self.hostname.split('.')[0]

    @staticmethod
    def _get_value(properties, property_name):
        """Get the value of property_name from within properties."""
        return properties.get(property_name) or 'N/A'

    def __lt__(self, other):
        """Perform comparison with another server. This is done by comparing capacity."""
        return self.capacity < other.capacity

    def __str__(self):
        """Get the string representation of this server."""
        return '{0}: {1} ({2})'.format(self.title, self.hostname, self.ip)

    def __repr__(self):
        """Get the debug string representation of this server."""
        return '\n'.join('{0}: {1}'.format(k, v) for k, v in self.__dict__.items())
