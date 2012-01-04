Walker
======

Goals
-----
This project aims to check other project directories with a set of rules. It
uses python 2.7, nosetest 2.7, and [PyYaml](http://pyyaml.org/).

How to run
----------

Check a project:

    ./walker

In this case it will look for a file named _walker.conf_ in the project
directory. There are options to set different config files and project
directories.

Run tests

    ./walker test

Configuration
-------------

Configuration syntax is in [YAML](http://en.wikipedia.org/wiki/YAML).

    vars:
        authors: Authors

    rules:
        - FileExistsChecker:
            requiredFiles:
                - '%{project_path}/project-walker-core1'
                - '/project-walker-core2'
                - 'project-walker-core3'
                - 'interpol.py'
        - FileContainsChecker:
            files: '*.py'
            contains: ["Copyright %authors"]

The keys of the config are longest token matched, case and the characters -_ are ignored.
So one can write _f_ instead of _files_.

### Rules

In this section one can list the rules, which are used to check a project. It
begins with the name of a check. Each checker has different configuration
options, and each supports interpolation on different options. Generally it
can be sad that the _files_ option does not support interpolation just
globbing expressions.

### Vars

This is an optional section.

Here one can define variables used below in the configuration.


Emedding variables
------------------

Syntax for embedding variables is as follows:

    %var

or

    %{var}

Variable embedding supports substring and search and replace operations as
well:

    %identifier:2           # from second character on
    %identifier:2:3         # from second character two third
    %{identifier:foo:bar}   # replace foo to bar in string

Additional to the user defined variables there are several other pre defined
variables:

 * project - name of the project directory

 * project_path - full path of the project

 * file_name - file name with extension

 * name - file name without extension

 * extension - surprise, surprise :)

 * path - path to file

 * full_path - full path with file name

 * type - d / f depending whether file is a directory or not

Checks
------

### FileExistsChecker

Checks whether the files listed in _requiredFiles_ exist. The option supports
interpolation. If a path expression starts with _/_ it is taken for the
project root so these two are equivalent:

    /foo/baz
    %project_path/foo/baz

The path expression support globbing as well:

    **/foo/*/ba[zZ]

The checker support a _count_ option. The required files need to be present so
many times in the project. Default is one. The count must be matched exactly.

### FileContainsChecker

Checks whether files in _matches_ contain the strings in _contains_. The
contains option supports interpolation. Both matches, and contains support
lists or plain strings.

Setting the _caseSensitive_ option to _false_ turns off case sensitive matching.

## FileNameChecker

Checks whether the file name of _files_  matches pattern in _matches_.

## FilePropertyChecker

Checks whether the properties of _files_ holds true to the settings:

  * encoding - utf8
  * lineEnding - unix
  * whitespace - space
  * trailingWhitespace - false
  * lineLength - 120

File Inclusion / Exclusion
--------------------------

Files can be included with _files_ excluded with _excludeFiles_.

Development
-----------

Code is formatted with [PythonTidy](http://pypi.python.org/pypi/PythonTidy).

Authors
-------

* John Kliff Jochens
* Tamás Eppel

License
-------

All files licensed under the 3-clause BSD license, full text see in LICENSE.

Copyright
---------

2011, Authors
