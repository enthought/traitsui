The `upcoming` directory contains news fragments that will be added to the
changelog for the NEXT release.

Changes that are not of interest to the end-user can skip adding news fragment.

Add a news fragment
-------------------
Create a new file with a name like ``<pull-request>.<type>.rst``, where
``<pull-request>`` is a pull request number, and ``<type>`` is one of:

- ``feature``: New feature
- ``bugfix``: Bug fixes
- ``deprecation``: Deprecations of public API
- ``removal``: Removal of public API
- ``doc``: Documentation changes
- ``test``: Changes to test suite ('end users' are distribution packagers)
- ``build``: Build system changes that affect how the distribution is installed

Then write a short sentence in the file that describes the changes for the
end users, e.g. in ``123.removal.rst``::

    Remove package xyz.

Alternatively, use the following command, run from the project root directory
and answer the questions::

    python etstool.py changelog create

(This command requires ``click`` in the environment.)
