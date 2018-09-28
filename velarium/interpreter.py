import datetime
import ntpath
import os
import readline
import subprocess
import time
from builtins import input

import cmd2
import pick
from dateutil import parser

from . import color, network, process, utils
from .providers import providers

ASCII_LOGO = ''
VERSION_EXPIRATION_DAYS = 7


class Interpreter(cmd2.Cmd):
    """A simple line-oriented command interpreter for connecting to VPN providers."""
    app_dir = utils.get_app_dir()
    last_updated_file = os.path.join(app_dir, 'last_updated')
    provider_file = os.path.join(app_dir, 'last_provider')
    config_files = {}
    provider = None

    history_file = os.path.join(app_dir, '.history')
    history_file_size = 1000

    prompt_template_no_user = '{0}~: '
    prompt_template_user = '{0}@{1}~: '

    max_hosts_for_ping = 50
    ping_rtt_threshold_ms = 100

    open_vpn_process = None

    def preloop(self):
        if os.path.exists(self.history_file):
            readline.read_history_file(self.history_file)

        try:
            provider_name = None
            if os.path.isfile(self.provider_file):
                with open(self.provider_file, 'r') as provider_file:
                    provider_name = provider_file.readline()
                    self._set_provider(provider_name)

            if not provider_name:
                self.do_select()

            provider_config_files = []
            for root, _, files in os.walk(self.provider.config_dir):
                for config in files:
                    if config.endswith('.ovpn'):
                        provider_config_files.append(os.path.join(root, config))

            if not provider_config_files:
                should_update = utils.query_yes_no('Oops! No configuration (.ovpn) files found. Do you want to '
                                                   'download a set of configuration files?')
                if should_update:
                    self.do_update()

            self.config_files = {ntpath.basename(config_file): config_file for config_file in provider_config_files}
        except OSError:
            print('Failed to load config files from {0} directory. Consider calling update.'.format(
                self.provider.config_dir))
            self.config_files = {}

    def postloop(self):
        self._save_history()

    def do_clear_user(self, _=0):
        """Clear the OpenVPN username for the selected provider."""
        self.provider.clear_user()
        self._update_prompt()

    def do_set_user(self, username):
        """Set the OpenVPN username for the selected provider."""
        if not username:
            if utils.query_yes_no('Do you want to clear configured username for {0}?'.format(self.provider.get_name())):
                self.provider.clear_user()
        else:
            if utils.query_yes_no('Do you want to configure the IPVanish username to be {0}?'.format(
                    color.Color.bold(username))):
                self.provider.set_user(username)

        self._update_prompt()

    def do_select(self, provider_name=''):
        """Select VPN provider by name."""
        if not provider_name:
            provider_name, _ = pick.pick(providers.available_provider_names,
                                         '{0}\nSelect VPN provider.'.format(ASCII_LOGO),
                                         '=>')

        self._select_provider(provider_name)

    def _select_provider(self, provider_name):
        self._set_provider(provider_name)

        if not os.path.isdir(self.provider.config_dir):
            os.makedirs(self.provider.config_dir)

        with open(self.provider_file, 'w') as provider_file:
            provider_file.write(provider_name)

        self.do_update()

    def complete_select(self, text, line, _start_idx, _end_idx):
        return self._complete(text, line, providers.available_provider_names)

    def do_update(self, _=0):
        """Update selected provider."""
        self._save_history()

        self.provider.update()

        with open(self.last_updated_file, 'w') as new_last_updated:
            new_last_updated.write(time.strftime("%Y-%m-%d %H:%M"))

        process.relaunch()

    def do_connect(self, config_file):
        """Connect with the specified config_file to the selected provider."""
        if (not config_file) or (config_file.lower() == 'auto'):
            config_file = self._auto_select_server()

        print('Using config file {0}'.format(config_file))
        if config_file not in self.config_files.keys():
            print('Config file not found... Try calling update.')
            return

        try:
            self.provider.connect(self.config_files.get(config_file))
        finally:
            self._teardown()

    def complete_connect(self, text, line, _start_idx, _end_idx):
        """Return list of suggestions for TAB completion for connect method."""
        return self._complete(text, line, self.config_files.keys()[:])

    @classmethod
    def do_clear(cls, _=0):
        """Clear screen only showing the ASCII logo."""
        subprocess.call(['/usr/bin/clear'])
        print('\n {0}'.format(ASCII_LOGO.replace('\n', '\n ')))

    def do_add(self, provider_name):
        """Add a VPN provider."""
        while not provider_name:
            provider_name = input('Please enter provider name: ')

        configs_url = None
        while not configs_url:
            configs_url = input('Please the URL to a zip file with configuration files: ')

        with open(os.path.join(self.app_dir, 'providers.conf'), 'a') as providers_file:
            providers_file.write('{0}  :  {1}'.format(provider_name, configs_url))

        self.do_select(provider_name)

        process.relaunch()

    @classmethod
    def do_firewall(cls, toggle):
        """Set UFW rules to only allow incoming and outgoing traffic on interface tun0."""
        if not toggle:
            print('In order to toggle firewall, please call with "enable" or "disable"')
            return

        if toggle.lower() == 'enable':
            network.ufw_set()

        if toggle.lower() == 'disable':
            network.ufw_reset()

    def complete_firewall(self, text, line, _start_idx, _end_idx):
        return self._complete(text, line, ['enable', 'disable'])

    def _save_history(self):
        readline.set_history_length(self.history_file_size)
        readline.write_history_file(self.history_file)

    def _set_provider(self, provider_name):
        self.provider = providers.get_provider(provider_name, self.app_dir)
        if not self.provider:
            # Default to something. Note the use of do_select,
            # which in turns calls _set_provider. This is done
            # in order to update the providers file correctly
            self.do_select('IPVanish')

        self._update_prompt()

    def _update_prompt(self):
        provider_name = self.provider.get_name()

        username = self.provider.get_user()
        if username:
            self.prompt = self.prompt_template_user.format(self.provider.get_user(), provider_name)
        else:
            self.prompt = self.prompt_template_no_user.format(provider_name)

    def _auto_select_server(self):
        """Auto select server from selected provider."""
        print('Auto selecting server...')

        servers = self.provider.get_servers_filtered(self.max_hosts_for_ping, self.ping_rtt_threshold_ms)
        if not servers:
            return ''

        selection, _ = pick.pick(servers,
                                 title='{0}\nChoose host: '.format(ASCII_LOGO),
                                 indicator='=>')

        # Get the matching configuration file
        return next(config for config in self.config_files.keys()[:] if selection.config_selector in config)

    @staticmethod
    def _complete(text, line, available_completions):
        """Return list of suggestions for TAB completion for connect method."""
        if not text:
            completions = available_completions
        else:
            # Handle spaces in text (using partition in order to make successive TAB completions work)
            part = line.partition(' ')[2]
            offset = len(part) - len(text)
            completions = [c[offset:] for c in available_completions if c.lower().startswith(part.lower())]

        return completions

    @staticmethod
    def _teardown():
        """Kill deluge instances, reset UFW rules and kill openvpn instances."""
        if process.kill('deluge'):
            network.ufw_reset()

        process.kill('openvpn')


def run():
    global ASCII_LOGO

    subprocess.call(['/usr/bin/clear'])

    ASCII_LOGO = utils.get_ascii_logo()
    if ASCII_LOGO:
        # Start printing from (1,1) instead of (0,0) in order to follow the pick module
        print('\n {0}'.format(ASCII_LOGO.replace('\n', '\n ')))

    interpreter = Interpreter()
    if os.path.isfile(interpreter.last_updated_file):
        with open(interpreter.last_updated_file) as last_updated_file:
            last_updated = last_updated_file.read()
            # Auto-update if more than a week old
            if parser.parse(last_updated) < (
                    datetime.datetime.now() - datetime.timedelta(days=VERSION_EXPIRATION_DAYS)):
                if utils.query_yes_no('Last updated more than a week ago. Do you wish to update now?'):
                    interpreter.do_select()

            print('{0}\nLast updated: {1}\n{0}'.format('-{0}-'.format(
                '-'*len(ASCII_LOGO.splitlines()[-1])),
                last_updated))

    print(network.get_dns_info())
    interpreter.cmdloop()
