.. python-terminusgps documentation master file, created by
   sphinx-quickstart on Wed Feb 19 10:39:57 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-terminusgps documentation
================================

============
Installation
============

Use pip to install from `PyPI <https://pypi.org/project/python-terminusgps/>`_.

.. code:: bash

   pip install python-terminusgps

In Python, all subpackages are nested within :py:mod:`terminusgps`:

.. code:: python

   from terminusgps.aws.secrets import get_secret
   from terminusgps.wialon.session import WialonSession

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    settings.rst
    authorizenet/index.rst
    aws/index.rst
    twilio/index.rst
    wialon/index.rst
