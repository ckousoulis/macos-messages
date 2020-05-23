macOS Messages
==============

macOS Messages is an open source tool built to help macOS users manipulate
chat archives (.ichat files) managed by the Messages (previously iChat)
application.

With the command-line interface, anyone can merge chats from a backup into the
the main archive. The commands and user experience are modeled after diff and
merge tools commonly used in software development.

Running
-------

  from source:

  1. Clone the `macos-messages`_ repository.
  2. From the repository root directory, run:

    .. code-block:: text

      $ python -m messages ~/Library/Messages/Archive

  from install:

  1. ``pip install path/to/tarball``
  2. From anywhere within the Python environment, run:

    .. code-block:: text

      $ macos-messages ~/Library/Messages/Archive

3. Run commands to merge, inspect, and prepare changes to the target archive.
4. When ready, run ``flush`` to write the archive changes to disk.

.. _`macos-messages`: https://github.com/ckousoulis/macos-messages

Commands
--------

* ``list``: Displays the target archive and all sources opened with ``merge``.
* ``show``: Prints the current state of the target archive.
* ``merge path/to/archive``: Opens and merges a source archive into the target.
* ``diff``: Highlights changes the user needs to adjust or should inspect.
* ``search Word or Phrase``: Finds chats whose filenames include the terms.
* ``results``: Enumerates the full paths to chats that match the last search.
* ``ignore``: Marks the chats from the last search to be ignored in the merge.
* ``simulate``: Fakes a ``flush`` and displays its output to the console.
* ``flush``: Writes changes to disk and summary to ``messages_results.txt``.
* ``help``: Shows help text with a list of commands.
* ``quit``: Exits the shell, as does ``^d`` for end of file.

Developing
----------

* Install packages: ``lorem``, ``pylint``.
* Lint the source files in accordance with `Google's Style Guide`_.
* Create fake archives for testing commands with ``generate_archives.py``.
* Inspect the extended attributes of an archive with ``xattr_printer.py``.
* Package with ``python setup.py sdist``.

.. _`Google's Style Guide`: http://google.github.io/styleguide/pyguide.html