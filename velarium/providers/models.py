class Server(object):

    def __init__(self, title, hostname, config_selector):
        self.title = title
        self.hostname = hostname
        self.config_selector = config_selector
        self.rtt = -1

    def set_rtt(self, rtt):
        self.rtt = rtt

    def __str__(self):
        return self.title if self.rtt < 0 else '{0}, rtt={1}ms'.format(self.title, self.rtt)

    def __repr__(self):
        return self.__str__()
