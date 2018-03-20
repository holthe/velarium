from velarium.providers import baseprovider


class SimpleProvider(baseprovider.BaseProvider):

    def __init__(self, app_dir, name, configs_url):
        self._name = name
        self.configs_url = configs_url
        super(SimpleProvider, self).__init__(app_dir)

    def get_name(self):
        return self._name
