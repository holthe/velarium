import fcntl
import os
import pwd
import shlex
import subprocess
import sys

import utils

PID_FILE = None


def try_call(command, quiet=False):
    """Try to call the given command."""
    try:
        print('Calling {0}'.format(command))
        f_null = open(os.devnull, 'w') if quiet else None
        return subprocess.check_call(shlex.split(command),
                                     stdout=f_null,
                                     stderr=f_null,
                                     close_fds=True) == 0
    except subprocess.CalledProcessError:
        return False


def try_call_multiple(commands):
    """Try to call a list of commands stopping at the first error."""
    for command in commands:
        if not try_call(command):
            return False

    return True


def relaunch_with_sudo(force=False, interactive=False):
    """Re-launch current process as root with 'sudo'."""
    if force or os.geteuid() != 0:
        if interactive and not utils.query_yes_no('velarium needs root. Do you want to re-launch with sudo?'):
            return

        # os.execvp() replaces the running process, rather than launching a child
        # process, so there's no need to exit afterwards. The extra 'sudo' in the
        # second parameter is required because Python doesn't automatically set $0
        # in the new process.
        os.execvp('sudo', ['sudo'] + sys.argv)


def ensure_single_instance(process_name):
    """Ensure a single instance of the calling process by locking on a .pid file."""
    # PID_FILE must be global or the file will be closed after the function exits.
    global PID_FILE

    pid_file_name = '/var/run/{0}.pid'.format(process_name)
    PID_FILE = open(pid_file_name, 'w')
    try:
        fcntl.lockf(PID_FILE, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # Another instance is running
        print('Another instance is already running...')
        sys.exit(0)


def drop_privileges():
    """Drop privileges if root."""
    if os.getuid() != 0:
        # We're not root...
        return

    # Get the uid/gid from the name
    user_name = os.getenv('SUDO_USER')
    pwnam = pwd.getpwnam(user_name)

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)

    # Ensure a reasonable umask
    old_umask = os.umask(0o22)


def kill(process_name):
    """Kill process(es) with name process_name."""
    if not try_call('pgrep {0}'.format(process_name), quiet=True):
        print('No {0} instance to kill...'.format(process_name))
        return True
    else:
        print('Killing {0} instance(s)...'.format(process_name))
        return try_call('pkill {0}'.format(process_name), quiet=True)
