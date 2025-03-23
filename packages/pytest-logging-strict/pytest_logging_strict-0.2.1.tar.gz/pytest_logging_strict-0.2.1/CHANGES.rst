.. this will be appended to README.rst

Changelog
=========

..

   Feature request
   .................

   - `rst2html5 alternative <https://github.com/marianoguerra/rst2html5/>`_
     Not maintained package. Would require forking and maintaining
     In the interim, use docutils

   Known regressions
   ..................

   Commit items for NEXT VERSION
   ..............................

.. scriv-start-here

.. _changes_0-2-1:

Version 0.2.1 — 2025-03-23
--------------------------------

- tests: fix logging linesep same on Windows and posix
- feat: add fixture has_logging_occurred
- chore(pre-commit): add check typos
- chore: update wreck support
- ci: bump dependencies version

.. _changes_0-2-0:

Version 0.2.0 — 2025-01-19
--------------------------------

- feat: integrate logging-strict logging config registry API
- fix(requirements-dev): add nudge pin for package virtualenv to mitigate CVE-2024-53899
- ci(quality): build README.rst using rst2html5

.. _changes_0-1-0.post1:

Version 0.1.0.post1 — 2025-01-03
--------------------------------

- ci(test-coverage.yml): fix breaking change by codecov/codecov-action v5

.. _changes_0-1-0.post0:

Version 0.1.0.post0 — 2025-01-03
--------------------------------

- docs(README.rst): fix one link

.. _changes_0-1-0:

Version 0.1.0 — 2025-01-03
--------------------------

- fix(plugin): tempfile unlink ignore PermissionError on windows
- fix(tox.ini): target mypy wrong package name
- fix: after write flush tempfile or pypy will complain
- feat: pytest plugin for initializing logging
- chore: add pre-commit support
- chore: add Makefile
- chore: add tox support. format linting mypy pre-commit coverage wreck
- chore: add gh workflows

.. scriv-end-here
