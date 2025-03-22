edu-core-lib
============

Version: 0.3.4

Download   http://python.dev.tuttify.io/simple/

Keywords: library, edu, python

Installation
------------

::

    pip install --extra-index-url http://${PYPI_USERNAME}:${PYPI_PASSWORD}@python.dev.tuttify.io/simple --trusted-host python.dev.tuttify.io edu-core-lib



Package tests
-------------

To run test:

::

   pytest

Update and publish package:
---------------------------

1) change package version in ``setup.py`` file
2) run command to build package:

::

   python setup.py sdist

3) run command to upload new version on PyPI:

::

    twine upload   --repository-url  http://python.dev.tuttify.io dist/edu-core-lib-0.2.2.tar.gz
