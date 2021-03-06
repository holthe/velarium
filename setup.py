from setuptools import setup, find_packages

with open('README.rst') as f:
    velarium_readme = f.read()

with open('LICENSE.txt') as f:
    velarium_license = f.read()

setup(
    name='velarium',
    version='0.8.0',
    description='A simple line-oriented command interpreter for connecting to VPN providers.',
    long_description=velarium_readme,
    author='Peter Holthe Hansen',
    author_email='peter.holthe@gmail.com',
    url='https://github.com/holthe/velarium',
    license=velarium_license,
    keywords='velarium, vpn, openvpn, ipvanish, pia, purevpn, nordvpn, vyprvpn, hidemyass',
    packages=find_packages(exclude=['tests', 'docs']),
    package_data={
        'velarium': [
            'ascii_logo',
            'velarium.conf'
        ],
    },
    entry_points={
        'console_scripts': [
            'velarium=velarium:main',        # Expose interpreter command loop
            'unfirewall=velarium:ufw_reset'  # Expose functionality to reset UFW rules
        ],
    },
)
