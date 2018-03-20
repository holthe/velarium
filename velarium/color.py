class Color(object):
    """Class used for colouring terminal output."""

    def __init__(self):
        pass

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def bold(cls, string):
        """Return bold version of the given string."""
        return '{0}{1}{2}'.format(cls.BOLD, string, cls.END)