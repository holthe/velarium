import ipvanish

import config

available_providers = [
    ipvanish.IPVanish,
]

available_providers.extend([p for p in config.config.providers])

available_provider_names = [provider_cls.get_name() for provider_cls in available_providers]


def get_provider(provider_name, app_dir):
    match = next((provider for provider in available_providers if provider.get_name().lower() == provider_name.lower()),
                 None)
    if not match:
        return None

    if callable(match):
        return match(app_dir)
    else:
        return match
