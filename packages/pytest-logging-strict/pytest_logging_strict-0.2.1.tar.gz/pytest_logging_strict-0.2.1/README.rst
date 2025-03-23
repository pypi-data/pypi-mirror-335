pytest-logging-strict
======================

pytest fixture logging configured from packaged YAML

|  |kit| |license| |versions|
|  |test-status| |codecov| |quality-status|
|  |stars| |mastodon-msftcangoblowm|

.. PYVERSIONS

\* Python 3.9 through 3.13, PyPy

**New in 0.2.x**

registry implementation; add fixture has_logging_occurred;

**New in 0.1.x**

initial release;

Why?
-----

Every single test, of interest, has boilerplate to setup the logging
configuration or a shortcut to avoid it e.g. pytest fixture ``caplog``.

If there is a logging configuration, that comes from each package.
Somewhere, there is a logging configuration module or a call to
``logging.basicConfig``.

Logging boilerplate configuration code is dodgy, nonsense, hardcoded,
not portable, and hobbles usage of most built-in logging features.

- ``logging-strict`` -- Manages logging configurations by
  providing APIs to access both the registry and the logging config YAML
  files

- ``pytest-logging-strict`` -- adds pytest integration

With pytest integration:

- querying

  Once per pytest session. Query options are provided in
  ``pyproject.toml`` and cli options can override.

  Pulls the registry and logging config YAML from ``logging-strict``
  or third party package.

  Share your logging configuration. Can submit your logging config YAML
  file to ``logging-strict`` for curation.

- extracting

  Once per pytest session. Extracts into a session scoped temp folder.
  Afterwards, session registry and logging config YAML files are removed

- pytest fixture

  ``logging_strict`` fixture provides both the logger **and** list of
  all available loggers.

  So know which loggers are enabled besides only the main package logger

Installation
-------------

.. code:: shell

   python -m pip install pytest-logging-strict


Configuration
--------------

In ``conftest.py``

.. code:: shell

   pytest_plugins = ["logging_strict"]

In ``pyproject.toml``

Customize the query
""""""""""""""""""""

All query options are optional and have a default.

If no query options are provided, the result will be to use the
default logging strict YAML file. This is highly discouraged. Provide a query.

- yaml_package_name -- which package to use

  The default is ``yaml_package_name = 'logging-strict'``. But can curate
  logging config YAML in your own package or third party packages.
  This is burdensome and troublesome, so hoping to curate into one package.

- category -- app has additional dependencies, worker does not

  e.g. ``category = 'app'`` with ``genre = textual``
  **has additional dependency**, ``textual``

impl_version_no -- a coin flip of two unfortunite choices

- Do not provide it

  Use the latest implementation, which might introduce breakage.

- Provide it

  e.g. ``impl_version_no = '1'``

  Stick with a known to work safe implementation. At some later date,
  could be phased out, resulting in breakage.

There is no plan to introduce any more implementations

In ``pyproject.toml``

.. code:: shell

    [tool.pytest.ini_options]
    logging_strict_impl_version_no = '1'
    logging_strict_yaml_package_name = 'logging_strict'
    logging_strict_category = 'worker'
    logging_strict_genre = 'mp'
    logging_strict_flavor = 'asz'
    logging_strict_version_no = '1'

and/or cli

.. code:: shell

   pytest --showlocals -vv \
   --logging-strict-impl-version-no = '1' \
   --logging-strict-yaml-package-name = 'logging_strict' \
   --logging-strict-category = 'worker' \
   --logging-strict-genre = 'mp' \
   --logging-strict-flavor = 'asz' \
   --logging-strict-version-no = '1' tests

The cli overrides ``pyproject.toml`` settings.

impl_version_no 0
""""""""""""""""""

``impl_version_no 1`` introduced ``logging_config.yml`` registry for logging
config YAML files. The registry YAML file is strictly and safely validated.

This removed the need to worry about:

- In which subfolder the logging config YAML file resides

- the file name, following a strict naming convention and
  encoding meta data

The default impl_version_no is now 1. To use impl_version_no 0, both
impl_version_no and package_data_folder_start are required

In ``pyproject.toml``

.. code:: text

   logging_strict_impl_version_no = '0'
   logging_strict_package_data_folder_start = 'configs'

cli

.. code:: text

   --logging-strict-impl-version-no = '0' \
   --logging-strict-package-data-folder-start = 'configs'

``impl_version_no 0`` will be phased out as ``impl_version_no 1`` matures

Usage
------

Minimalistic example
"""""""""""""""""""""

pytest marker sends param ``package name`` to the fixture.
Creates the main logger instance. While still having access to
all possible loggers defined in the logger config YAML file. e.g. ``root``
and ``asyncio``.

.. code:: text

   import pytest

   @pytest.mark.logging_package_name("my_package_name")
   def test_fcn(logging_strict):
       t_two = logging_strict()
       if t_two is not None:
           logger, lst_loggers = t_two
           logger.info("Hello World!")

The pytest marker communicates ur package name to logging_strict fixture.
Which then initiates the main logger instance.

Full example
"""""""""""""

.. code:: text

   import logging
   from logging_strict.tech_niques import captureLogs
   import pytest

   @pytest.mark.logging_package_name("my_package_name")
   def test_fcn(logging_strict):
       t_two = logging_strict()
       if t_two is None:
           logger_name_actual == "root"
           fcn = logger.error
       else:
           assert isinstance(t_two, tuple)
           logger, lst_loggers = t_two
           logger_name_actual = logger.name
           logger_level_name_actual = logging.getLevelName(logger.level)

           msg = "Hello World!"

           # log message was logged and can confirm
           with captureLogs(
               logger_name_actual,
               level=logger_level_name_actual,
           ) as cm:
               fcn(msg)
           out = cm.output
           is_found = False
           for msg_full in out:
               if msg_full.endswith(msg):
                   is_found = True
           assert is_found

Batteries included
-------------------

**textual console apps**

As mentioned previously, ``category = 'app'`` with ``genre = 'textual'``
logging config has additional dependency, ``textual``.

Trying to use a logging config without first the installing the required
dependency, ``textual``, results in an Exception and traceback.

.. code:: shell

   pytest --showlocals -vv \
   --logging-strict-yaml-package-name = 'logging_strict' \
   --logging-strict-category = 'app' \
   --logging-strict-genre = 'textual' \
   --logging-strict-flavor = 'asz' \
   --logging-strict-version-no = '1' tests

``--logging-strict-impl-version-no = '1'`` is optional

**multiprocess worker** -- use as default

``category = 'worker'`` is to query logging config that
**do not require any additional dependencies**.

.. code:: shell

   pytest --showlocals -vv \
   --logging-strict-yaml-package-name = 'logging_strict' \
   --logging-strict-category = 'worker' \
   --logging-strict-genre = 'mp' \
   --logging-strict-flavor = 'asz' \
   --logging-strict-version-no = '1' tests

Please submit your logging configuration for review and curation to
make available to everyone.

In the meantime or if not in the mood to share

.. code:: shell

   pytest --showlocals -vv \
   --logging-strict-yaml-package-name = 'zope.interface' \
   --logging-strict-category = 'worker' \
   --logging-strict-genre = 'mp' \
   --logging-strict-flavor = 'mine' \
   --logging-strict-version-no = '1' tests

The package data file would be stored as:

``data/mp_1_mine.worker.logging.config.yaml``

The flavor, e.g. ``mine``, should be alphanumeric no whitespace nor underscores.
e.g. ``justonebigblob``

Milestones
-----------

- Simplify querying

  Support for a registry of logging config YAML records.

  The registry is a package data file, ``logging_config.yml``

  HISTORY

  `logging-strict#4 <https://github.com/msftcangoblowm/logging-strict/issues/4>`_

  logging-strict-1.5.0 adds registry API

  support added in 0.2.0

- classifier

  pypi.org allows searching by classifiers. So will be easier for everyone
  to identify which packages offer logging config YAML files

License
--------

aGPLv3+ `[full text] <https://github.com/msftcangoblowm/logging-strict/blob/master/LICENSE.txt>`_

Collaborators
--------------

Note *there is no code of conduct*. Will **adapt to survive** any mean
tweets or dodgy behavior.

Can collaborate by:

ACTUALLY DO SOMETHING ... ANYTHING

- use ``pytest-logging-strict`` in your own packages' tests
- peer review and criticism. Make me cry, beg for leniency, and have
  no other recourse than to appeal to whats left of your humanity
- request features
- submit issues
- submit PRs
- follow on mastodon. Dropping messages to **say hello** or share
  offensive memes
- translate the docs into other languages
- leave a github star on repos you like
- write distribute and market articles to raise awareness

ASK FOR HELP

- ask for eyeballs to review your repo
- request for support

FOSS FUNDING

- apply force and coercion to ensure maintenance continues. Funding
  should be unencumbered. This are accepted: monero or litecoin

- fund travel to come out to speak at tech conferences (reside in West Japan)

- Hey Mr. Money McBags printer goes Brrrrr! Protest your tech stack by
  identifying package maintainers in need of funding.
  Ask which package maintainers are starving and planning retribution

ASK FOR ABUSE

- Throw shade, negativity, and FUD at everything and anything. Do it!
  Will publicly shame you into put your money where your mouth is.

- pointless rambling and noise that leads no where. Will play spot the
  pattern and respond with unpleasant truths, or worse, offensive memes

- Threaten to be useful or hold higher standing. e.g. recruiters or NPOs/NGOs

- suggest a code of conduct. Ewwwww! That's just down right mean

- suggest a license written by a drunkard

.. |test-status| image:: https://github.com/msftcangoblowm/pytest-logging-strict/actions/workflows/testsuite.yml/badge.svg?branch=master&event=push
    :target: https://github.com/msftcangoblowm/pytest-logging-strict/actions/workflows/testsuite.yml
    :alt: Test suite status
.. |quality-status| image:: https://github.com/msftcangoblowm/pytest-logging-strict/actions/workflows/quality.yml/badge.svg?branch=master&event=push
    :target: https://github.com/msftcangoblowm/pytest-logging-strict/actions/workflows/quality.yml
    :alt: Quality check status
.. |kit| image:: https://img.shields.io/pypi/v/pytest-logging-strict
    :target: https://pypi.org/project/pytest-logging-strict/
    :alt: PyPI status
.. |versions| image:: https://img.shields.io/pypi/pyversions/pytest-logging-strict.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/pytest-logging-strict/
    :alt: Python versions supported
.. |license| image:: https://img.shields.io/github/license/msftcangoblowm/pytest-logging-strict
    :target: https://pypi.org/project/pytest-logging-strict/blob/master/LICENSE.txt
    :alt: License
.. |stars| image:: https://img.shields.io/github/stars/msftcangoblowm/pytest-logging-strict.svg?logo=github
    :target: https://github.com/msftcangoblowm/pytest-logging-strict/stargazers
    :alt: GitHub stars
.. |mastodon-msftcangoblowm| image:: https://img.shields.io/mastodon/follow/112019041247183249
    :target: https://mastodon.social/@msftcangoblowme
    :alt: msftcangoblowme on Mastodon
.. |codecov| image:: https://codecov.io/gh/msftcangoblowm/pytest-logging-strict/graph/badge.svg?token=3aE90WoGKg
    :target: https://codecov.io/gh/msftcangoblowm/pytest-logging-strict
    :alt: pytest-logging-strict coverage percentage
