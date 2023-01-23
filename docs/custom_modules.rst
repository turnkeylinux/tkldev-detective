TKLDev-Detective Custom Modules
===============================

Custom modules are simply python files, with 1 or more class definitions that
subclass ``FileClassifier`` or ``FileLinter`` residing inside of the
``tkldet_modules`` directory.

(Non-file classifiers and linters might be possible but are not yet
officially supported)

XXX ReportFilters are also possible to subclass once fully implemented

Common Notes
------------

One thing that all custom operational models share is a concept of "weight"
which is used to determine the order that each check is done in.

By default all of these classes contain a class-variable ``WEIGHT: int``.

Counter-intuitively classes are used in ascending order of weight, the
recommended weight for situations that do not require specific ordering is
``100``. 

Custom Classifiers
------------------

Classifiers are very simple by design, here's a very simple example of a
classifier which tags directories, it's only job is to take an ``Item``
and if it refers to a directory, tag it with a relevant tag.

.. code-block:: python3

    from libtkldet.classifier import FileClassifier, FileItem, register_classifier
    from os.path import isdir

    @register_classifier # this line registers our custom class to be used as a classifier
    class DirectoryClassifier(FileClassifier):
        WEIGHT: int = 80
        # we want this to run earlier than most classifier,
        # but not necessarily first so we reduce the weight by 20

        def classify(self, item: FileItem):
            # classify is the only method you MUST implement when deriving from
            # FileClassifier, it does not return anything

            if isdir(item):
                item.add_tags(self, ['directory'])
                # we pass a reference to ourselves, so the item can keep track
                # of which tags came from which classifiers
                #
                # we also pass a list of as many tags as we wish to add to this
                # item. The exact value of our tag is unimportant, only that it
                # doesn't conflict with any other tags.

See ``filetype.py``, ``shebang.py`` for more examples of custom classifiers.

Helper Classifiers
~~~~~~~~~~~~~~~~~~

There are currently 2 helper classifiers, ``ExactPathClassifier`` and
``SubdirClassifier``.

ExactPathClassifier classifies only a single file item with a specific path, to
use it you simply need to set a few required class variables:

.. code-block:: python3

    from libtkldet.classifier import ExactPathClassifier, register_classifier

    @register_classifier
    class CustomExactPathClassifier(ExactPathClassifier):
        path: str = "path/to/some/file"
        # exact location of file, relative to appliance root

        tags: list[str] = [ "tag1", "tag2" ]
        # all these tags are added to the specific file matched

SubdirClassifier is only marginally more complex, it will tag all files that are
directory descendants of the given path, optionally recursively.

.. code-block:: python3

    from libtkldet.classifier import SubdirClassifier, register_classifier

    @register_classifier
    class CustomSubdirClassifier(SubdirClassifier):
        path: str = "path/to/some/file"
        # exact location of parent directory, relative to appliance root

        tags: list[str] = [ "tag1", "tag2" ]
        # all these tags are added to children of directory

        recursive: bool = True
        # recurse into child directories?

Too see examples of these helper classifiers see the ``appliance_files.py``
module.

Custom Linters
--------------

Linters are a little more complex, but ultimately quite similar.

Here's an example of a linter that produces an info report for every line
that contains "TODO" 

.. code-block:: python3

    from libtkldet.linter import FileLinter, register_linter
    from libtkldet.report import FileReport, ReportLevel
    from typing import Generator

    @register_linter
    class TodoLinter(FileLinter):
        ENABLE_TAGS: set[str] = set()
        DISABLE_TAGS: set[str] = set()

        # by default, linter will only run when either:
        #
        # 1. ENABLE_TAGS is empty and there is no overlap between item tags and 
        #    DISABLE_TAGS
        # 2. ENABLE_TAGS is not-empty, at least 1 tag from ENABLE_TAGS is
        #    included in the given item, and no items from DISABLE_TAGS are
        #    present


        WEIGHT: int = 100
        # weight here works the same as classifiers


        def check(self, item: Item) -> Generator[Report, None, None]:
            # note this is a generator, we "yield" reports

            with open(item.abspath) as fob:
                for i, line in enumerate(fob):
                    if 'TODO' in line:
                        yield FileReport(
                            item=item, # same item as input

                            line=i,
                            column=line.find('TODO'),
                            # both line or column can be a single integer, a
                            # tuple of integers or ommited entirely. However
                            # if line number is ommited, column should be too

                            location_metadata=None,
                            # currently populated by  meta info that doessn't
                            # fit elseware, not output currently

                            message = 'Found todo NOTE: " + line.split('TODO', 1)[1],
                            # the message shown to user

                            fix = None,
                            # suggested fix as a string if known/relevant
                            # otherwise None

                            source = 'TodoLinter',
                            # arbitrary string to represent the linter that
                            # found this issue

                            level = ReportLevel.INFO
                            # kind of report level, 1 for all the standard log
                            # levels as well as "CONVENTION" and "REFACTOR"
                            # (possibly more as time goes on)
                        )

If the logic surrounding ``ENABLE_TAGS`` and ``DISABLE_TAGS`` is insufficient to
determine if the linter should run you can override ``Linter.should_check``
method which actually performs those checks it takes the ``Item`` as an argument
and returns a boolean indicating if the linter should check the item.
