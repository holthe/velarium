import ntpath
import os
import shutil

import interpreter
import network
import utils


def ufw_reset():
    """Reset UFW rules."""
    network.ufw_reset()


def main():
    """Entry point for the application script."""
    # We need to run as root and we only allow a single instance
    process.relaunch_with_sudo(interactive=True)
    process.ensure_single_instance('velarium')

    #shutil.copy(utils.configuration_file,
    #            os.path.join(app_dir, ntpath.basename(utils.configuration_file)))

    interpreter.run()
