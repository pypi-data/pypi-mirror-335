COMPLETE REFACTOR --------- LAST WORKING VERSION HERE
=====================================================

Project codeframe
=================

*Creates a simple package structure, Fire, git, PyPI, bumpversion,
pytest and configfile ready*

Introduction
------------

To create a new python project is a bit tedious task, especially if one
doesn\'t know how to.

This purpose of this package is to make a simple, but still functional
project structure.

Installation
------------

`pip3 install codeframe`

Usage
-----

Try just:

`codeframe myproject myunit`

This will create:

-   subdirectory named `myproject` and inside:
-   **hardlink** to `bin/myproject` named `bin_myproject`,
-   unit `myunit`, that is soft-linked as `test_myunit`, so it works
    with `pytest`,
-   `version.py`, that works with `bumpversion`
-   subsubdirectory `myproject`, that contains softlinks to `../` so
    that the package structure works
-   `setup.py` file, where you need to fill the requirements list and
    other things
-   `README.org`, that will generate `README.md` when `./distcheck` is
    run
-   with `config` module it **creates** a new config DIR
    `~/.config/myproject`
-   and some less important stuff

Highlights:
-----------

1.  The modules should be callable in `jupyter` that is opened in the
    `myproj` directory.
2.  The hardlink `bin_myproject` make the script inside `bin/` callable
    (but git pull from elsewhere looses the hardlink!)
3.  Installable on local system with the usual command
    `pip3 install -e .`
4.  `config` module can be both - used at a new project and imported
    from any project `from codeframe import config`

./distcheck
-----------

-   generates `README.md`
-   creates git commit
-   bumpversion release
-   pushes to PyPI

Notes for development
---------------------

Thanks to `Fire`, each module can be developed separately and CLI can be
finally tuned in `bin/myproject` (hard-linked to `bin_myproject`) file.

TODO
====

-   topbar from gregory
-   key~enter~ \'\'
