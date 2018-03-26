from . import interpreter, network, process


def ufw_reset():
    """Reset UFW rules."""
    network.ufw_reset()


def main():
    """Entry point for the application script."""
    # We need to run as root and we only allow a single instance
    process.relaunch_with_sudo(interactive=True)
    process.ensure_single_instance('velarium')

    interpreter.run()
