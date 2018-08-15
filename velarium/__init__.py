from . import interpreter, network, process


def ufw_reset():
    """Reset UFW rules."""
    network.ufw_reset()


def main():
    """Entry point for the application script."""
    # We only allow a single instance
    process.ensure_single_instance('velarium')

    interpreter.run()
