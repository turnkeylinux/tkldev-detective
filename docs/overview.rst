TKLDev-Detective Overview
=========================

tkldev-detective is actually pretty simple, it boils down to 6 concepts, 2 data
models and 4 "operational" models which function in serial.

Data models
-----------

Item
    An item is just a piece of unspecified data accompanied by a set of tags.

    Subtypes of item are used to distinguish between concrete concepts,
    currently the only type of ``Item`` supported is ``FileItem`` which (as you
    might assume) contains a path as it's data.

Report
    A report is the final piece of data to be shown to the user. It contains
    various pieces of information about a potential issue, how serious it is,
    information relating to where it is, what potential fixes might be
    available and what linter found this issue.

    Just like Item's this type is intended to be subclassed for other types of
    data, and just like ``FileItem``; ``FileReport`` is currently the only such
    subclass. It provides sufficient information to show file snippets related
    to issues in a variety of ways contextual to how much information it's given
    about the location of the issue inside the file.

Operational models
------------------

Locator
    the "Locator" determines which files are checked in the first place
    in the future this will provide a broader concept of "checkable thing" than
    just file, for now though we can safely only consider files.

    The locator produces "Items", these are a model that contains some kind of
    "data" (here because they are just files, the data is the path itself)
    and can be tagged.

Classifier
    the "Classifier" determines various qualities about a certain file, these
    qualities or classifications are referred to internally as "tags".

    An example of a tag might be ``shebang:/usr/bin/python3`` which asserts that
    this file has a shebang, and that the shebang is for python3. Note, the use
    of ``shebang:`` prefix as there is infinite variation in shebangs.

    Some tags though have no variation, such is the case for
    ``appliance-makefile`` which is only set for the top-level ``Makefile``
    found in an appliance.

Linter
    the "Linter" performs checks on the inputted "items" and yields any number
    of "Reports". Linter's are the most diverse of these groups.

    Examples of linters go from ``PyLinter`` and ``Shellcheck``, linter's which
    wrap the 3rd-party linters "pylint" and "shellcheck" respectively, all the
    way through ``JsonLint`` which just loads json files and yields a report if
    loading fails.

ReportFilter
    the "ReportFilter" is the last stop for reports before they are presented
    to the user. A ``ReportFilter`` is mostly intended to remove false
    positives but can also be used to add additional context to reports in a
    way that might not make sense in the linter itself or even to modify reports
    completely if necessary.
