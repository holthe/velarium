import os
import subprocess
import zipfile

import velarium.network
from . import models, ping


class BaseProvider(object):

    configs_url = None

    def __init__(self, app_dir):
        self.config_dir = os.path.join(app_dir, self.get_name().lower(), 'configs')
        self.auth_file = os.path.join(self.config_dir, '..', 'user_pass_auth.conf')
        self.cert_file = self._find_file_with_ext('.crt')
        self.pem_file = self._find_file_with_ext('.pem')
        self._additional_connection_arguments = []

    @staticmethod
    def get_name():
        raise NotImplementedError()

    def get_user(self):
        if os.path.isfile(self.auth_file):
            with open(self.auth_file, 'r') as up:
                return up.readline()
        return ''

    def clear_user(self):
        if os.path.isfile(self.auth_file):
            os.remove(self.auth_file)

    def set_user(self, username):
        """Set OpenVPN username."""
        with open(self.auth_file, 'w') as up:
            up.write(username)

        # Auth file should only be accessible by its owner.
        os.chmod(self.auth_file, 0o600)

    def get_servers_filtered(self, max_hosts_for_ping, ping_rtt_threshold_ms):
        servers_for_ping = self._get_servers()

        ping_results = ping.PingSweeper(ping_rtt_threshold_ms).sweep(
            [server.hostname for server in servers_for_ping[:min(len(servers_for_ping), max_hosts_for_ping)]])

        best_results = sorted(
            [result for result in ping_results if result.ping_rtt < ping_rtt_threshold_ms],
            key=lambda x: x[1])

        best_servers = [server for server in servers_for_ping if
                        server.hostname in [result.host for result in best_results]]

        for server in best_servers:
            server.set_rtt(
                next(result for result in ping_results if result.host == server.hostname).ping_rtt)

        return sorted(best_servers, key=lambda s: s.rtt)

    def connect(self, config_file):
        script_file = '/etc/openvpn/update-resolv-conf'
        security_level = 2
        verbose_level = 3
        cmd = ['sudo',
               'openvpn',
               '--config', os.path.join(self.config_dir, config_file),
               '--script-security', str(security_level),
               '--up', script_file,
               '--down', script_file,
               '--verb', str(verbose_level)]

        if os.path.isfile(self.auth_file):
            cmd.extend(('--auth-user-pass', self.auth_file))

        if self.cert_file:
            cmd.extend(('--ca', self.cert_file))

        if self.pem_file:
            cmd.extend(('--crl-verify', self.pem_file))

        for argument in self._additional_connection_arguments:
            cmd.extend(argument)

        print(cmd)
        process = None
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for stdout_line in iter(process.stdout.readline, ''):
                print(stdout_line)
                if 'Initialization Sequence Completed' in stdout_line:
                    velarium.network.ufw_set()
                    print(velarium.network.get_dns_info())
        except KeyboardInterrupt:
            print('\nCaught CTRL+C...')
        except Exception as err:
            print('\n[!] Caught exception: {0}'.format(err))
        finally:
            if process:
                process.stdout.close()

    def _get_servers(self):
        """Get servers by parsing configuration files. Override if needed."""
        config_files = [c for c in os.listdir(self.config_dir) if c.endswith('.ovpn')]

        servers = []
        for config_file in config_files:
            with open(os.path.join(self.config_dir, config_file), 'r') as f:
                lines = f.readlines()
                hostname = next(line for line in lines if line.startswith('remote')).split(' ')[1]
                title = '{0}: {1}'.format(config_file.split('.')[0], hostname)
                servers.append(models.Server(title, hostname, config_file))

        return servers

    def update(self):
        """Download and extract config files from the given url. Override if needed."""
        with velarium.network.download(self.configs_url) as configs_zip_mem_file:
            with zipfile.ZipFile(configs_zip_mem_file) as zip_file:
                zip_file.extractall(self.config_dir)

    def _find_file_with_ext(self, ext):
        """Find first file with the given extension."""
        match = None
        for root, _, files in os.walk(self.config_dir):
            match = next((f for f in files if f.endswith(ext)), None)
            if match:
                match = os.path.join(root, match)
                break

        return match

    def _add_connection_argument(self, switch, parameter):
        """Add an additional connection argument."""
        self._additional_connection_arguments.append((switch, parameter))
