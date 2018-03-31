.. highlight:: rst

.. |master| image:: https://travis-ci.org/holthe/velarium.svg?branch=master
    :target: https://travis-ci.org/holthe/velarium

.. |review| image:: https://api.codacy.com/project/badge/Grade/fed7566940164fbf9e4be7eaf758870f
   :target: https://www.codacy.com/app/holthe/velarium?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=holthe/velarium&amp;utm_campaign=Badge_Grade

.. |license| image:: http://img.shields.io/:license-MIT-red.svg
   :target: LICENSE.txt

====================================
velarium |master| |review| |license|
====================================

A simple line-oriented command interpreter for connecting to VPN providers.

^^^^^^
Status
^^^^^^

.. |develop| image:: https://travis-ci.org/holthe/velarium.svg?branch=develop
    :target: https://travis-ci.org/holthe/velarium

+---------+-----------+
| Branch  | Status    |
+=========+===========+
| master  | |master|  |
+---------+-----------+
| develop | |develop| |
+---------+-----------+

^^^^^^^^^^^^^^^^^^^
Supported providers
^^^^^^^^^^^^^^^^^^^

* IPVanish
* Private Internet Access
* HideMyAss
* PureVPN
* NordVPN
* VyprVPN

^^^^^^^^^^^^^^^^
Adding providers
^^^^^^^^^^^^^^^^

Adding a *simple* VPN provider can be done by dropping a ``providers.conf`` file in ``~/.config/velarium/``. The format is the same as in `velarium/providers.conf <velarium/providers.conf>`_, i.e. the configuration file needs a ``[providers]`` header and each provider is configured on a single line with two ``:``-separated columns, ``{NAME} : {CONFIGS_URL}``.
