TKLDev-Detective
================

tkldev-detective is a simple framework for linting turnkeylinux appliances, it
leverages existing linting tools, as well as allowing for custom handmade lints
and provides a unified output format/interface for utilizing these tools.

Dependencies
~~~~~~~~~~~~

tkldev-detective has no mandatory dependencies

Currently though there is 1 optional dependency:

    pyyaml - enables yaml lint

Installation
------------

tkldev-detective can be installed as follows

1. Clone somewhere, I recommend cloning into ``/turnkey/public`` (creating
   intermediate directories as required)

    .. code-block:: bash

        mkdir -p /turnkey/public
        git clone git@github.com:turnkeylinux/tkldev-detective /turnkey/public/tkldev-detective

2. Add ``tkldev-detective`` to your path:

   .. code-block:: bash

        ln -s /turnkey/public/tkldev-detective/tkldev-detective /usr/local/bin

Usage
-----

Using ``tkldev-detective`` is as simple as running
``tkldev-detective lint <appliance>`` where ``<appliance>`` can be the name of
an appliance or the path to an appliance, provided you have the appliance
build-code present on your tkldev.

E.g.

``tkldev-detective lint zoneminder``

For more information on how it works and how to develop more functionality, see
`overview`_ and `custom modules`_

Copyright
---------

This file is part of tkldev-detective.

tkldev-detective is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

tkldev-detective is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with tkldev-detective. If not, see <https://www.gnu.org/licenses/>.

.. _overview: ./docs/overview.rst
.. _custom modules: ./docs/custom_modules.rst
