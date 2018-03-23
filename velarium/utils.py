import subprocess
import sys
from contextlib import contextmanager

import appdirs
import pkg_resources

configuration_file = pkg_resources.resource_filename('velarium', 'providers.conf')


def get_app_dir():
    return appdirs.user_config_dir('velarium')


@contextmanager
def get_resource(resource_name):
    """Get the resource with the given name."""
    f = open(pkg_resources.resource_filename('velarium', resource_name), 'r')
    try:
        yield f
    finally:
        f.close()


def get_ascii_logo():
    """Get the ascii logo."""
    _, columns = subprocess.check_output(['/bin/stty', 'size']).split()
    with get_resource('ascii_logo') as ascii_logo:
        if len(max(ascii_logo, key=len)) <= int(columns):
            # We need to seek back, because the file has already been read
            ascii_logo.seek(0)
            return ascii_logo.read()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    try:
        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
    except KeyboardInterrupt:
        print('')


