import fcntl
import os
import subprocess
import sys

from . import utils

PID_FILE = None


def try_call(command, quiet=False):
    """Try to call the given command."""
    try:
        print('Calling {0}'.format(command))
        f_null = open(os.devnull, 'w') if quiet else None
        return subprocess.check_call(command,
                                     stdout=f_null,
                                     stderr=f_null,
                                     close_fds=True) == 0
    except subprocess.CalledProcessError:
        return False


def try_call_multiple(*commands):
    """Try to call a list of commands stopping at the first error."""
    for command in commands:
        if not try_call(command):
            return False

    return True


def ensure_single_instance(process_name):
    """Ensure a single instance of the calling process by locking on a .pid file."""
    # PID_FILE must be global or the file will be closed after the function exits.
    global PID_FILE

    pid_file_name = os.path.join(utils.get_app_dir(), '{0}.pid'.format(process_name))
    PID_FILE = open(pid_file_name, 'w')
    try:
        fcntl.lockf(PID_FILE, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # Another instance is running
        print('Another instance is already running...')
        sys.exit(0)


def relaunch():
    # TODO PHH 15-sep-2018: Implement this...
    pass


def kill(process_name):
    """Kill process(es) with name process_name."""
    if not try_call(['pgrep', process_name], quiet=True):
        print('No {0} instance to kill...'.format(process_name))
        return True
    else:
        print('Killing {0} instance(s)...'.format(process_name))
        return try_call(['pkill', process_name], quiet=True)
