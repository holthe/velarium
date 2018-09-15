import collections
import json
import random
from contextlib import contextmanager
from io import BytesIO

import requests
import tqdm

from . import color, process


def ufw_set():
    """Set UFW rules to only allow incoming and outgoing traffic on interface tun0."""
    return process.try_call_multiple(['sudo', 'ufw', '--force', 'reset'],
                                     ['sudo', 'ufw', 'default', 'deny', 'incoming'],
                                     ['sudo', 'ufw', 'default', 'deny', 'outgoing'],
                                     ['sudo', 'ufw', 'allow', 'out', 'on', 'tun0', 'from', 'any', 'to', 'any'],
                                     ['sudo', 'ufw', 'enable'])


def ufw_reset():
    """Reset UFW rules."""
    return process.try_call_multiple(['sudo', 'ufw', '--force', 'reset'],
                                     ['sudo', 'ufw', 'default', 'deny', 'incoming'],
                                     ['sudo', 'ufw', 'default', 'allow', 'outgoing'],
                                     ['sudo', 'ufw', 'enable'])


@contextmanager
def download(url, chunk=True, verbose=True):
    """Download the content of the given url and returns it in a StringIO object."""
    if verbose:
        print('Retrieving {0}'.format(url))

    try:
        response = requests.get(url, stream=True)
    except Exception as e:
        print('No connection...')
        return

    out_handle = BytesIO()
    content_length = response.headers.get('Content-Length')
    if (content_length is None) or (not chunk):
        out_handle.write(response.content)
    else:
        chunk_size = 256
        bars = int(int(content_length) / chunk_size)

        progress_bar = tqdm.tqdm(response.iter_content(chunk_size=chunk_size),
                                 total=bars,
                                 unit='B',
                                 desc=url[url.rfind("/") + 1:],
                                 leave=True)

        for data in progress_bar:
            out_handle.write(data)

    try:
        yield out_handle
    finally:
        out_handle.close()


def get_dns_info():
    """Get DNS info retrieved from https://{hash}.ipleak.net/json/ where {hash} is a 40 char random hash."""
    result = ''
    for _ in range(3):
        try:
            # Generate a random 40 char hash used for making ipleak do a 'mydns' query type
            dns_test_url = 'https://%032x.ipleak.net/json/\n' % random.getrandbits(160)
            print('\nRetrieving DNS info\n{0}'.format(dns_test_url))

            with download(dns_test_url, chunk=False, verbose=False) as ip_info_mem_file:
                data = ip_info_mem_file.getvalue()

            ip_dict = json.loads(data.decode('utf-8'), object_pairs_hook=collections.OrderedDict)

            result = ''
            error = False
            for k, v in ip_dict.items():
                if str(k).lower() == 'error':
                    error = True
                    break
                result += '{0}: {1}\n'.format(color.Color.bold(k.replace('_', ' ').capitalize()), v or 'N/A')

            if not error:
                break
        except:
            return ''

    return result
