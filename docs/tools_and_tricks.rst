Tools and Tricks
================

A number of utilities are provided in ``libtkldet`` intended for use in modules.

Note all of these modules are described *without* the preceding ``libtkldet.``
you would usually see these listed as for brevity's sake;

Common Info
-----------

.. note:: 

    Not to be mistaken as a general use of the word "common" this refers
    specifically to fab common directory found at ``${FAB_PATH}/common``
    (usually ``/turnkey/fab/common``)

``common_data``
    contains a variety of functions to get info about which parts of common
    are being used.

``common_data.is_package_to_be_installed(package_name: str) -> bool``
    checks if a package will be installed during build from plan, packages
    installed outside of the plan are not considered by this function

``common_data.is_common_plan_included(plan_name: str) -> bool``
    checks if a common plan, specifically whatever is found at
    ``${FAB_PATH}/common/plans/${plan_name}`` is included in the current build

``common_data.get_common_overlays() -> list[str]``
    returns list of all common overlays included in this appliance

``common_data.get_common_conf() -> list[str]``
    returns list of all common conf scripts included in this appliance

``common_data.get_common_removelists() -> list[str]``
    returns list of all common removelists included in this appliance

``common_data.get_common_removelists() -> list[str]``
    returns list of all common removelists_final included in this appliance
    (same as above but run after appliance specific conf scripts)

``common_data.get_path_in_common_overlay(path: str) -> Optional[str]``
    given a path relative to appliance root (e.g.
    ``/etc/apache2/sites-available/foobar.conf``) return absolute path to the
    common file/dir inside the common overlay.

Apt File
--------

``apt_file``
    contains a variety of functions relating too figuring out what packages
    provide what *things*

``apt_file.find_package_by_file(path: str) -> list[str]``
    provides a list of packages that provide a file/directory specified by the
    given path.

``apt_file.find_python_package(package_name: str) -> list[str]``
    provides a list of packages which provide a given python package,
    specifically what provides
    ``/usr/lib/python3/dist-packages/{package_name}``.

    Usually ``find_python_package_from_import`` is more applicable.

``apt_file.find_python_package_from_import(module_str: str) -> list[str]``
    provides a list of packages which provide a given python module,
    module can be of any depth ``foo.bar.baz`` will work just as well as
    ``foo.bar`` and in the off-chance more specific modules are provided by
    unique packages, this function will choose the most specific package for the
    module provided.



Fuzzy Match/Search
------------------

.. note::

    Currently this uses a **VERY** basic home-rolled heuristic for judging how
    close words are.

``fuzzy.fuzzy_diff(a: str, b: str) -> int``
    calculates some heuristic "difference" between 2 strings. The value itself
    is arbitrary and only to be used in comparison.

``fuzzy.fuzzy_suggest(check: str, options: list[str]) -> Optional[str]``
    given a ``check`` value, and a list of options, produces the option
    (deemed by heuristic) to be the closest to the ``check`` value or None
    if none are deemed close enough.
