# Copyright (c) Turnkey GNU/Linux <admin@turnkeylinux.org>
#
# this file is part of tkldev-detective.
#
# tkldev-detective is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# tkldev-detective is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# tkldev-detective. If not, see <https://www.gnu.org/licenses/>.
import json
from typing import Generator
import subprocess

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, FileReport, parse_report_level
from libtkldet.apt_file import is_in_path

RUFF_LINTS = dict(
    pyflakes = dict(
        F401 = 'WARN',  # unused import
        F402 = 'WARN',  # import shadowed by loop variable
        F403 = 'WARN',  # import * used
        F404 = 'ERROR', # late __future__ import
        F405 = 'WARN',  # possibly undefined (unsure due to import *)
        F406 = 'ERROR', # import * used outside module level
        F407 = 'ERROR', # unknown __future__ import

        F501 = 'ERROR', # invalid % formatting
        F502 = 'ERROR', # % expected mapping, got sequence
        F503 = 'ERROR', # % expected sequence, got mapping
        F504 = 'ERROR', # % has unused name arguments
        F505 = 'ERROR', # % has missing arguments
        F506 = 'ERROR', # % mixed positional and named
        F507 = 'ERROR', # % positional count mismatch
        F508 = 'ERROR', # % * specifier requires sequence
        F509 = 'ERROR', # % unsupported format char

        F521 = 'ERROR', # .format invalid format string
        F522 = 'ERROR', # .format unused name arguments
        F523 = 'ERROR', # .format unused positional arguments
        F524 = 'ERROR', # .format missing arguments
        F525 = 'ERROR', # .format mix automatic and manual numbering

        F541 = 'REFACTOR', # fstring no placeholders
        
        F601 = 'ERROR', # dict key literal repeated
        F602 = 'WARN',  # dict key variable repeated
        
        F621 = 'ERROR', # too many expressions in star unpacking
        F622 = 'ERROR', # two starred expressions in assignment

        F631 = 'WARN',  # assert is non-empty tuple
        F632 = 'ERROR', # == checking 2 constant literals
        F633 = 'ERROR', # >> used with print
        F634 = 'WARN',  # if tuple check (always true)
        
        F701 = 'ERROR', # break outside loop
        F702 = 'ERROR', # continue outside loop

        F704 = 'ERROR', # yield outside function

        F706 = 'ERROR', # return outside function
        F707 = 'ERROR', # default except not last

        F722 = 'ERROR', # invalid type annotation

        F811 = 'WARN',  # redefined of unused variable

        F821 = 'ERROR', # undefined variable
        F822 = 'ERROR', # undefined name in __all__
        F823 = 'ERROR', # local variable undefined 
        
        F841 = 'WARN', # unused variable
        F842 = 'WARN', # annotated but never used

        F901 = 'WARN', # incorrect raise NotImplementedError
    ),
    pycodestyle = dict(
        E101 = 'ERROR', # mixed spaces and tabs

        E111 = 'ERROR', # bad indent
        E112 = 'ERROR', # expected indented block
        E113 = 'ERROR', # unexpected indentation
        E114 = 'ERROR', # bad indent (with comment)
        E115 = 'ERROR', # expected indent block (with comment)
        E116 = 'ERROR', # unexpected indentation (with comment)
        E117 = 'ERROR', # over indented (with comment)

        E201 = 'CONVENTION', # whitespace after open bracket
        E202 = 'CONVENTION', # whitespace before close bracket
        E203 = 'CONVENTION', # whitespace before punctuation
        E204 = 'CONVENTION', # whitespace after decorator
        
        E211 = 'CONVENTION', # whitespace before parameters

        E221 = 'CONVENTION', # multiple whitespace before operator
        E222 = 'CONVENTION', # multiple whitespace after operator
        E223 = 'CONVENTION', # tab before operator
        E224 = 'CONVENTION', # tab after operator
        E225 = 'CONVENTION', # missing whitespace around operator
        E226 = 'CONVENTION', # missing whitespace around arithmetic operator
        E227 = 'CONVENTION', # missing whitespace around bitwise operator
        E228 = 'CONVENTION', # missing whitespace around modulo operator

        E231 = 'CONVENTION', # missing whitespace

        E241 = 'CONVENTION', # multiple spaces after comma
        E242 = 'CONVENTION', # tab after comma

        E251 = 'CONVENTION', # unexpected spaces around keyword / param equals
        E252 = 'CONVENTION', # missing whitespace around param equals
        
        E261 = None, # too few spaces before comment
        E262 = 'CONVENTION', # inline comment missing space

        E265 = 'CONVENTION', # block comment missing space
        E266 = 'CONVENTION', # too many # before block comment

        E271 = 'CONVENTION', # too many spaces after keyword
        E272 = 'CONVENTION', # too many spaces before keyword
        E273 = 'CONVENTION', # tab after keyword
        E274 = 'CONVENTION', # tab before keyword
        E275 = 'CONVENTION', # missing whitespace after keyword

        E301 = 'CONVENTION', # wrong number blank line between methods
        E302 = 'CONVENTION', # wrong number blank lines top of module
        E303 = 'CONVENTION', # too many blank lines
        E304 = 'CONVENTION', # blank lines after decorator
        E305 = 'CONVENTION', # wrong number blank lines after class/func
        E306 = 'CONVENTION', # missing blank line before nested definition

        E401 = 'CONVENTION', # multiple imports on one line
        E402 = 'CONVENTION', # module level import not at top of cell
        
        E501 = 'CONVENTION', # line too long
        E502 = 'CONVENTION', # redundant backslash
        
        E701 = 'CONVENTION', # multiple statements on one line (colon)
        E702 = 'CONVENTION', # multiple statements on one line (semicoloon)
        E703 = 'CONVENTION', # unnecessary semicolon

        E711 = 'CONVENTION', # `== None` used instead of `is None`
        E712 = 'CONVENTION', # `==` used with `True` / `False`
        E713 = 'CONVENTION', # `not (? in ?)` used instead of `? not in ?`
        E714 = 'CONVENTION', # `not (? is ?)` used instead of `? is not ?`

        E721 = 'CONVENTION', # `type(?) == ?` used instead of `isinstance(?)`
        E722 = 'CONVENTION', # bare except used
    
        E731 = 'CONVENTION', # assigned lambda instead of def
        
        E741 = 'CONVENTION', # ambigious variable name
        E742 = 'CONVENTION', # ambigious class name
        E743 = 'CONVENTION', # ambigious function name

        E902 = 'ERROR', # io error
        E999 = 'ERROR', # syntax error

        W191 = 'CONVENTION', # uses tabs for indentation

        W291 = 'CONVENTION', # trailing whitespace
        W292 = 'CONVENTION', # missing newline at EOF
        W293 = 'CONVENTION', # blank line with whitespace

        W391 = 'CONVENTION', # too many newlines at EOF

        W505 = 'CONVENTION', # doc line too long

        W605 = 'ERROR', # invalid escape sequence
    ),
    mccabe = dict(
        C901 = 'REFACTOR', # structure too complex
    ),
    isort = dict(
        I001 = 'CONVENTION', # unsorted imports
        I002 = 'ERROR', # missing required import
    ),
    pep8_naming = dict(
        N801 = 'CONVENTION', # bad class name
        N802 = 'CONVENTION', # bad func name
        N803 = 'CONVENTION', # bad arg name
        N804 = 'ERROR', # bad cls argument
        N805 = 'ERROR', # bad self argument
        N806 = 'CONVENTION', # bad local var name
        N807 = 'CONVENTION', # non-standard dunder method

        N811 = 'CONVENTION', # const imported as non const
        N812 = 'CONVENTION', # lowercase imported as non lowercase
        N813 = 'CONVENTION', # camelcase imported as non lowercase
        N814 = 'CONVENTION', # camelcase imported as constant
        N815 = 'CONVENTION', # class variable using mixedcase
        N816 = 'CONVENTION', # global variable using mixedcase
        N817 = 'CONVENTION', # camelcase imported as acronym
        N818 = 'CONVENTION', # exception name not suffixed "Error"

        N999 = 'CONVENTION', # invalid module name
    ),
    pydocstyle = dict(
        D100 = 'CONVENTION', # missing docstring in module
        D101 = 'CONVENTION', # missing docstring in class
        D102 = 'CONVENTION', # missing docstring in method
        D103 = 'CONVENTION', # missing docstring in function
        D104 = 'CONVENTION', # missing docstring in package
        D105 = 'CONVENTION', # missing docstring in magic method
        D106 = 'CONVENTION', # missing docstring in nested class
        D107 = 'CONVENTION', # missing docstring in __init__
        
        D200 = 'CONVENTION', # one line docstring not on one line
        D201 = None, # (conflicts D211) blank line before func docstring
        D202 = 'CONVENTION', # blank line after func docstring
        D203 = 'CONVENTION', # missing blank line before class docstring
        D204 = 'CONVENTION', # missing blank line after class docstring
        D206 = 'CONVENTION', # missing blank line between summary and description in docstring
        D207 = 'CONVENTION', # under-indented docstring
        D208 = 'CONVENTION', # over-indented docstring
        D209 = 'CONVENTION', # multi-line docstring should close on seperate line
        D210 = 'CONVENTION', # whitespace surrounding docstring text
        D211 = 'CONVENTION', # blank line before class docstring
        D212 = None, # (conflicts D213) multi-line summary not on first line
        D213 = 'CONVENTION', # docstring multi-line summary not on first line 
        D214 = 'CONVENTION', # docstring section over-indented
        D215 = 'CONVENTION', # docstring section underline is over-indented

        D300 = 'CONVENTION', # docstring should use triple double-quotes (""")
        D301 = 'CONVENTION', # docstring should use raw triple double-quotes (r""") if backslash in docstring

        D400 = None, # docstring first line should end with '.'
        D401 = 'CONVENTION', # docstring first line should be in imperative mood
        D402 = 'CONVENTION', # docstring first line shoudl not be in function's signature
        D403 = 'CONVENTION', # first word of line should be capitalized in docstring
        D404 = 'CONVENTION', # docstring should not start with "This"
        D405 = 'CONVENTION', # docstring section name should be capitalized
        D406 = 'CONVENTION', # docstring section name should end with newline
        D407 = 'CONVENTION', # docstring missing dashed underline after section name
        D408 = 'CONVENTION', # docstring section underline should be directly after section name
        D409 = 'CONVENTION', # docstring section underline should match length of section name
        D410 = 'CONVENTION', # missing newline after docstring section
        D411 = 'CONVENTION', # missing newline before docstring section
        D412 = 'CONVENTION', # missing blank line between docstring section header and contents
        D413 = 'CONVENTION', # missing blank line after last docstring section
        D414 = 'CONVENTION', # docstring section has no contents
        D415 = None, # docstring first line should end with punctuation
        D416 = None, # docstring section name should end with a colon
        D417 = 'CONVENTION', # docstring missing argument description
        D418 = 'CONVENTION', # func decorated with `@overload` shouldn't contain docstring
        D419 = 'CONVENTION', # docstring is empty
    ),
    pyupgrade = dict(
        UP001 = 'REFACTOR', # `__metaclass__ = type` (implied)

        UP003 = 'REFACTOR', # type of primitive used instead of type name `type(1)` instead of `int`
        UP004 = 'REFACTOR', # class inheriting from object (implied)
        UP005 = 'REFACTOR', # deprecated unittest aliases used
        UP006 = 'REFACTOR', # pre pip858 annotation
        UP007 = 'REFACTOR', # pre pip604 union annotations
        UP008 = 'REFACTOR', # using `super(__class__, self)` instead of `super()`
        UP009 = 'REFACTOR', # UTF-8 declaration (implied)
        UP010 = 'REFACTOR', # unnecessary `__future__` import
        UP011 = 'REFACTOR', # unnecessary parentheses to `functools.lru_cache`
        UP012 = 'REFACTOR', # unnecessary call to encode as UTF-8
        UP013 = 'REFACTOR', # named dict should use class syntax
        UP014 = 'REFACTOR', # named tuples should use class syntax
        UP015 = None, # redundant `open(..., 'r')` when read mode is default

        UP017 = 'REFACTOR', # should use datetime.UTC alias for datetime.timezone.utc
        UP018 = 'REFACTOR', # unnecessary literal-type call to literal `str("foo")`
        UP019 = 'REFACTOR', # use of `typing.Text` instead of `str`
        UP020 = 'REFACTOR', # use of `io.open` instead of `open` builtin alias
        UP021 = 'REFACTOR', # use of `universal_newlines` kwarg instead of `text` to subprocess
        UP022 = 'REFACTOR', # use of `stdout=PIPE` and `stderr=PIPE` instead of `capture_output` in subprocess
        UP023 = 'REFACTOR', # use of `cElementTree` instead of `ElementTree` in `xml.etree`
        UP024 = 'REFACTOR', # use of exception that aliases `OSError`
        UP025 = 'REFACTOR', # use of unicode literal string
        UP026 = 'REFACTOR', # use of `mock` instead of `unittest.mock`
        UP027 = 'REFACTOR', # use of unpacked list comprehension instead of generator expression
        UP028 = 'REFACTOR', # use of yield only for loop instead of `yield from`
        UP029 = 'REFACTOR', # importing builtin
        UP030 = 'REFACTOR', # explicit positional format where implicit is correct
        UP031 = 'REFACTOR', # use of percent format instead of `.format`
        UP032 = 'REFACTOR', # use of `.format` instead of f-string
        UP033 = 'REFACTOR', # use of `functools.lru_cache` with `maxsize=None`
        UP034 = 'REFACTOR', # extra parentheses
        UP035 = 'REFACTOR', # use of deprecated import
        UP036 = None, # use of version-block test
        UP037 = 'REFACTOR', # use of unnecessary quoted annotation
        UP038 = 'REFACTOR', # use of `isinstance(..., (a, b))` instead of `isinstance(..., a | b)`
        UP039 = 'REFACTOR', # use of unnecessary parenthesis after class definition
        UP040 = 'REFACTOR', # use of `TypeAlias` instead of `type` keyword
        UP041 = 'REFACTOR', # use of aliases to `TimeoutError`
        UP042 = 'REFACTOR', # multiple inheritence instead of `StrEnum`
        UP043 = 'REFACTOR', # unnecessary default args for typing
    ),
    flake8_2020 = dict(
        YTT101 = 'REFACTOR', # `sys.version[:3]` instead of `sys.version_info`
        YTT102 = 'REFACTOR', # `sys.version[2]` instead of `sys.version_info`
        YTT103 = 'REFACTOR', # `sys.version` instead of `sys.version_info`

        YTT201 = None, # `sys.version_info[0] ==` instead of `sys.version_info[0] >=`
        YTT202 = 'REFACTOR', # `six.PY3` checked over `not six.PY2`
        YTT203 = 'REFACTOR', # `sys.version_info[1]` compared to integer instead of tuple
        YTT204 = 'REFACTOR', # `sys.version_info.minor` compared to integer instead of tuple
        
        YTT301 = 'REFACTOR', # `sys.version[0]` referenced instead of `sys.version_info`
        YTT302 = 'REFACTOR', # `sys.version` compared to string, instead of `sys.version_info`
        YTT303 = 'REFACTOR', # `sys.version[:1]` referenced instead of `sys.version_info`

    ),
    flake8_annotations = dict(
        # NOTE do we want to ensure typing in inithooks?
        ANN001 = 'REFACTOR', # missing type annotation for func arg
        ANN002 = 'REFACTOR', # missing type annotation for `*args`
        ANN003 = 'REFACTOR', # missing type annotation for `**kwargs`

        ANN101 = None, # missing type annotation for `self`
        ANN102 = None, # missing type annotation for `cls`

        ANN201 = 'REFACTOR', # missing return type annotation for public func
        ANN202 = 'REFACTOR', # missing return type annotation for private func

        ANN204 = 'REFACTOR', # missing return type annotation for special method
        ANN205 = 'REFACTOR', # missing return type annotation for static method
        ANN206 = 'REFACTOR', # missing return type annotation for class method

        ANN401 = 'REFACTOR', # use of dynamically typed expression
    ),
    flake8_async = dict(
        ASYNC100 = 'REFACTOR', # `async with` used with no internal `await`
        
        ASYNC105 = 'REFACTOR', # trio called without await

        ASYNC109 = 'REFACTOR', # async function with timeout param
        ASYNC110 = 'REFACTOR', # async busy wait

        ASYNC115 = 'REFACTOR', # use of sleep(0) in async
        ASYNC116 = 'REFACTOR', # async use of `sleep` with very large time, instead of `sleep_forever()`

        ASYNC210 = 'REFACTOR', # async function using blocking http methods

        ASYNC220 = 'REFACTOR', # async function using blocking create subprocess methods
        ASYNC221 = 'REFACTOR', # async function using blocking run subprocess methods
        ASYNC222 = 'REFACTOR', # async function using blocking wait on subprocess

        ASYNC230 = 'REFACTOR', # async function opening file with blocking methods

        ASYNC251 = 'REFACTOR', # async function calling `time.sleep`
    ),
    flake8_bandit = dict(
        S101 = None, # use of assert
        S102 = 'SECURITY', # use of exec
        S103 = 'SECURITY', # chmod setting overly permissive mask
        S104 = 'SECURITY', # address binding to 0.0.0.0
        S105 = 'SECURITY', # hardcoded password
        S106 = 'SECURITY', # hardcoded password in argument
        S107 = 'SECURITY', # hardcoded password in function default
        S108 = 'SECURITY', # hardcoded temp file

        S110 = 'SECURITY', # hardcoded try-except-pass (exception not logged)

        S112 = 'SECURITY', # hardcoded try-except-continue (exception not logged)
        S113 = 'SECURITY', # request without timeout (might wait forever)

        S201 = 'SECURITY', # use of `debug=True` with flask
        S202 = 'SECURITY', # use of `tarfile.extractall()`
        
        S301 = 'SECURITY', # possibly insecure use of pickle
        S302 = 'SECURITY', # possibly insecure use of marshal
        S303 = 'SECURITY', # use of MD2, MD4, MD5, SHA1
        S304 = 'SECURITY', # use of insecure cipher
        S305 = 'SECURITY', # use of insecure block cipher mode
        S306 = 'SECURITY', # use of `mktemp`
        S307 = 'SECURITY', # use of `eval`
        S308 = 'SECURITY', # use of `mark_safe`

        S310 = 'SECURITY', # use of unchecked URL
        S311 = 'SECURITY', # use of standard prng for crypto
        S312 = 'SECURITY', # use of telnet
        S313 = 'SECURITY', # use of xmlc etree
        S314 = 'SECURITY', # use of xml etree
        S315 = 'SECURITY', # use of xml expat reader
        S316 = 'SECURITY', # use of xml expat builder
        S317 = 'SECURITY', # use of xml sax
        S318 = 'SECURITY', # use of xml mini dom
        S319 = 'SECURITY', # use of xml pull dom
        S320 = 'SECURITY', # use of xmle etree
        S321 = 'SECURITY', # use of ftp

        S323 = 'SECURITY', # use of ssl `_create_unverified_context`
        S324 = 'SECURITY', # use of insecure hash functions

        S401 = 'SECURITY', # import of telnetlib
        S402 = 'SECURITY', # import of ftplib
        S403 = 'SECURITY', # use of pickle, cPickle, dill or shelve
        S404 = None, # import of subprocess
        S405 = 'SECURITY', # import of xml.etree
        S406 = 'SECURITY', # import of xml.sax
        S407 = 'SECURITY', # import of xml.dom.expatbuilder
        S408 = 'SECURITY', # import of xml.dom.minidom
        S409 = 'SECURITY', # import of xml.dom.pulldom
        S410 = None, # import of lxml, note this should be disabled anyway as lxml has addressed insecurities
        S411 = 'SECURITY', # import of xmlrpc
        S412 = 'SECURITY', # import of httpoxy
        S413 = 'SECURITY', # import of pycrypto, publicly disclosed buffer overflow
        S415 = 'SECURITY', # use of ipmi

        S501 = 'SECURITY', # ssl with disabled cert checks
        S502 = 'SECURITY', # insecure ssl protocol
        S503 = 'SECURITY', # ssl with bad defaults
        S504 = 'SECURITY', # ssl without version specified
        S505 = 'SECURITY', # weak crypto key size
        S506 = 'SECURITY', # unsafe yaml loader
        S507 = 'SECURITY', # paramiko ssh without host verification
        S508 = 'SECURITY', # insecure snmp version
        S509 = 'SECURITY', # snmp weak crypto
        
        S601 = 'SECURITY', # paramiko call
        S602 = 'SECURITY', # subprocess popen with shell=True
        S603 = None, # subprocess popen use at all
        S604 = 'SECURITY', # func call with shell=True
        S605 = 'SECURITY', # starting process with shell=True
        S606 = None, # starting process without shell
        S607 = 'SECURITY', # starting process with partial executable path
        S608 = 'SECURITY', # hardcoded sql expression
        S609 = 'SECURITY', # possible wildcard injection
        S610 = 'SECURITY', # django `extra` use (can lead to SQL injection)
        S611 = 'SECURITY', # django `RawSQL` use (can lead to SQL injection)
        S612 = 'SECURITY', # use of insecure `logging.config.listen`
        
        S701 = 'SECURITY', # use of jinja2 templates with `autoescape=False` 
        S702 = 'SECURITY', # use of mako templates
    ),
    flake8_blint_except = dict(
        BLE001 = 'WARN', # blind `except`
    ),
    flake8_boolean_trap = dict(
        FTB001 = None, # boolean typed positional arg in function def
        FTB002 = None, # boolean default positional argument in func def
        FTB003 = 'REFACTOR', # boolean positional value in func call
    ),
    flake8_bugbear = dict(
        B002 = 'ERROR', # unary prefix increment/decrement
        B003 = 'ERROR', # assignment to `os.environ`
        B004 = 'WARN',  # using `hasattr(x, '__call__')` instead of `callable(x)`
        B005 = 'WARN',  # `.strip()` with multicharacter string is misleading
        B006 = 'ERROR', # mutable default argument to function
        B007 = 'REFACTOR', # unused loop control variable
        B008 = 'REFACTOR', # function call in default argument
        B009 = 'REFACTOR', # getattr with constant attribute value
        B010 = 'REFACTOR', # setattr with constant attribute value
        B011 = 'REFACTOR', # use of `assert(False)`
        B012 = 'REFACTOR', # jump in except
        B013 = 'REFACTOR', # redundant tuple in except
        B014 = 'WARN',  # duplicate exception handler in `except`
        B015 = 'WARN',  # useless comparison
        B016 = 'ERROR', # raise literal
        B017 = 'ERROR', # `assertRaises(Exception, ...)`  
        B018 = 'ERROR', # useless expression
        B019 = 'ERROR', # use of `functools.lru_cache` or `functools.cache` on method
        B020 = 'WARN',  # loop control variable overrides iterable
        B021 = 'ERROR', # f-docstring (doesn't do what you think)
        B022 = 'REFACTOR', # useless contextlib suppress
        B023 = 'ERROR', # function defined in loop does not bind loop variable
        B024 = 'REFACTOR', # abstract base class without abstract methods
        B025 = 'ERROR', # duplicate try-except block
        B026 = 'ERROR', # star unpack after keyword arg
        B027 = 'ERROR', # empty method in abstract class
        B028 = 'WARN',  # `warnings.warn` without `stacklevel`
        B029 = 'ERROR', # except with empty tuple
        B030 = 'ERROR', # except with non-exception class
        B031 = 'ERROR', # reuse of groupby generator
        B032 = 'WARN',  # possible accidental type annotation
        B033 = 'ERROR', # duplicate item in set
        B034 = 'REFACTOR', # potentially confusing use of positional arg with some `re.*` functions
        B035 = 'ERROR', # dictionary comprehension with static key

        B039 = 'ERROR', # mutable default to contextvar

        B901 = 'ERROR', # return in generator

        B904 = 'ERROR', # raise without `from` inside exception handler (stops traceback propogating properly)
        B905 = 'WARN',  # zip without `strict=True` will truncate when iterables are of different lengths

        B909 = 'ERROR', # mutation of loop iterable
    ),
    flake8_builtins = dict(
        A001 = 'WARN', # variable shadows builtin
        A002 = 'WARN', # argument shadows builtin
        A003 = 'WARN', # class attribute shadows builtin
        A004 = 'WARN', # import shadows builtin
        A005 = 'WARN', # module shadows builtin
        A006 = 'WARN', # lambda argument shadows builtin
    ),
    flake8_commas = dict(
        COM812 = None, # missing trailing comma in sequence
        COM818 = 'ERROR', # trailing comma on bare tuple
        COM819 = None, # missing trailing comma in tuple
    ),
    flake8_copyright = dict(
        CPY001 = None, # missing copyright notice at top of file
    ),
    flake8_comprehensions = dict(
        C400 = 'REFACTOR', # unnecessary generator (could be `list()`)
        C401 = 'REFACTOR', # unnecessary generator (could be `set()`)
        C402 = 'REFACTOR', # unnecessary generator (could be dict comprehension)
        C403 = 'REFACTOR', # unnecessary list comprehension (could be set comprehension)
        C404 = 'REFACTOR', # unnecessary list comprehension (could be dict comprehension)
        C405 = 'REFACTOR', # unnecessary literal, use literal set instead
        C406 = 'REFACTOR', # unnecessary literal, use literal dict instead

        C408 = 'REFACTOR', # unnecessary literal call, use literal instead
        C409 = 'REFACTOR', # unnecessary list literal passed to tuple, use literal tuple instead
        C410 = 'REFACTOR', # unnecessary list literal passed to `list()` (remove outer list call)
        C411 = 'REFACTOR', # same as C410, but catches list comprehension

        C413 = 'REFACTOR', # unnecessary call around sorted (`list(...)` or `reversed(...)`)
        C414 = 'REFACTOR', # unnecessary double cast
        C415 = 'REFACTOR', # unnecessary subscript reversal
        C416 = 'REFACTOR', # unnecessary comprehension
        C417 = 'REFACTOR', # unnecessary map
        C418 = 'REFACTOR', # unnecessary dict literal passed to `dict()` (remove outer dict call)
        C419 = 'REFACTOR', # unnecessary list comprehension
        C420 = 'REFACTOR', # unnecessary dict comprehension for iterable (use dict.fromkeys instead)
    ),
    flake8_datetimez = dict(
        DTZ001 = 'WARN', # `datetime.datetime(...)` without `tzinfo` argument
        DTZ002 = 'WARN', # naive `datetime.datetime.today()` used
        DTZ003 = 'WARN', # naive `datetime.datetime.utcnow()` used
        DTZ004 = 'WARN', # naive `datetime.datetime.utcfromtimestamp()` used
        DTZ005 = 'WARN', # `datetime.datetime.now(...)` without `tz` argument
        DTZ006 = 'WARN', # `datetime.datetime.fromtimestamp(...)` without `tz` argument
        DTZ007 = 'WARN', # naive datetime constructed using `datetime.datetime.strptime()`

        DTZ011 = 'WARN', # naive `datetime.date.today()` used
        DTZ012 = 'WARN', # naive `datetime.date.fromtimestamp()` used
    ),
    flake8_debugger = dict(
        T100 = 'WARN', # debug trace or breakpoint found
    ),
    flake8_django = dict(
        DJ001 = 'REFACTOR', # `null=True` on string-based field

        DJ003 = 'REFACTOR', # use of `locals()` as context in reader function

        DJ006 = 'REFACTOR', # use of `exclude` instead of `fields` in `ModelForm`
        DJ007 = 'REFACTOR', # use of `__all__` instead of `fields` in `ModelForm`
        DJ008 = 'REFACTOR', # model doesn't define `__str__`

        DJ012 = 'CONVENTION', # order of model's inner classes, methods and fields does not follow django style guide
        DJ013 = 'ERROR', # `@receiver` must be on top of all other decorators
    ),
    flake8_errmsg = dict(
        EM101 = 'REFACTOR', # raw string in exception (shows twice in traceback)
        EM102 = 'REFACTOR', # f-string in exception (shows twice in traceback)
        EM103 = 'REFACTOR', # .format in exception (shows twice in traceback)
    ),
    flake8_executable = dict(
        EXE001 = 'WARN', # shebang is present but file is not executable
        EXE002 = 'WARN', # file is executable but shebang is not present
        EXE003 = 'WARN', # shebang doesn't contain "python"
        EXE004 = 'WARN', # shebang has leading whitespace
        EXE005 = 'WARN', # shebang not on first line
    ),
    flake8_future_annotations = dict(
        FA100 = 'WARN', # uses old annotations rather than importing `__future__.annotations`
        FA102 = None,   # uses new annotations and doesn't import `__future__.annotations`
    ),
    flake8_implicit_str_concat = dict(
        ISC001 = 'REFACTOR', # implicit str concat on one line
        ISC002 = 'REFACTOR', # implicit str concat over multiple lines
        ISC003 = 'REFACTOR', # explicit str concat could be implicit str concat
    ),
    flake8_import_conventions = dict(
        ICN001 = 'CONVENTION', # not using conventional import alias
        ICN002 = 'CONVENTION', # using explicitly non-conventional import alias
        ICN003 = 'CONVENTION', # using explicitly non-conventional import from instead of alias
    ),
    flake8_logging = dict(
        LOG001 = 'WARN', # using `logger.Logger` directly
        LOG002 = 'WARN', # using `__cached__` or `__file__` for logger name
        LOG003 = 'WARN', # using `logger.exception` without `exc_info`
        LOG004 = 'REFACTOR', # using `logging.WARN`
    ),
    flake8_logging_format = dict(
        G001 = 'REFACTOR', # logging statement uses `.format`
        G002 = 'REFACTOR', # logging statement uses `%` formatting
        G003 = 'REFACTOR', # logging statement uses `+` string concatenation
        G004 = 'REFACTOR', # logging statement uses f-string formatting
        G010 = 'REFACTOR', # logging uses `.warn` instead of `.warning`

        G101 = 'WARN', # logging uses an `extra` field that conflicts with a `LogRecord` field

        G201 = 'REFACTOR', # logging `.error(..., exc_info=True)` instead of `.exception(...)`
        G202 = 'REFACTOR', # logging statement has redundant `exc_info`
    ),
    flake8_no_pep420 = dict(
        INP001 = 'REFACTOR', # package missing an `__init__.py`
    ),
    flake8_pie = dict(
        PIE790 = 'REFACTOR', # unnecessary `pass` statement

        PIE794 = 'WARN', # class field defined multiple times

        PIE796 = 'WARN', # enum contains duplicate value

        PIE800 = 'REFACTOR', # unnecessary dict spread

        PIE804 = 'WARN', # unnecessary `**` kwargs
        
        PIE807 = 'REFACTOR', # unnecessary `lambda` in dataclass field
        PIE808 = 'REFACTOR', # unnecessary `range` start argument

        PIE810 = 'REFACTOR', # multiple `.startswith` or `.endswith` calls
    ),
    flake8_print = dict(
        T201 = None, # `print` call found
        T202 = None, # `pprint` call found
    ),
    flake8_pyi = dict(
        PYI001 = 'REFACTOR', # private type param should start with `_`
        PYI002 = 'REFACTOR', # overly complex `sys.version_info` comparison
        PYI003 = 'WARN', # bad `sys.version_info` check
        PYI004 = 'WARN', # `sys.version_info` patch version check
        PYI005 = 'WARN', # incorrect tuple length in `sys.version_info` comparison
        PYI006 = 'WARN', # bad `sys.version_info` check
        PYI007 = 'WARN', # bad `sys.platform` check
        PYI008 = 'WARN', # unrecognized `sys.platform` name
        PYI009 = 'REFACTOR', # using `pass` instead of `...` in stub block
        PYI010 = 'WARN', # non-empty stub block
        PYI011 = 'WARN', # non-trivial default value
        PYI012 = 'WARN', # pass in class body
        PYI013 = 'WARN', # non-empty class body contains `...` in stub
        PYI014 = 'WARN', # complex default value for argument in stub
        PYI015 = 'WARN', # complex default value for assignment in stub
        PYI016 = 'WARN', # duplicate union member
        PYI017 = 'WARN', # complex assignment in stub
        PYI018 = 'WARN', # unused private type var
        PYI019 = 'REFACTOR', # custom type var return instead of `typing.Self`
        PYI020 = 'WARN', # quoted annotation in stub
        PYI021 = 'WARN', # docstring in stub

        PYI024 = 'WARN', # `collections.namedtuple` instead of `typing.NamedTuple` in stub
        PYI025 = 'CONVENTION', # use of unaliased `collections.abc.Set`
        PYI026 = 'WARN', # type alias without `typing.TypeAlias` type

        PYI029 = 'REFACTOR', # explicitly defined method which is always implicitly defined in stub
        PYI030 = 'REFACTOR', # unnecessary literal union

        PYI032 = 'WARN', # `typing.Any` used in `__eq__` or `__ne__` instead of `object`
        PYI033 = 'REFACTOR', # comment in stub file
        PYI034 = 'WARN', # non-self return type in `__new__`
        PYI035 = 'WARN', # unassigned special variables
        PYI036 = 'WARN', # bad typing in `__exit__` or `__aexit__` in stub

        PYI041 = 'REFACTOR', # redundant numeric union
        PYI042 = 'CONVENTION', # type alias should be CamelCase
        PYI043 = 'CONVENTION', # private type alias should not be suffixed with `T`
        PYI044 = 'REFACTOR', # `__future__.annotations` don't effect stubs
        PYI045 = 'WARN', # `__aiter__` returns incorrect type
        PYI046 = 'WARN', # private protocol never used
        PYI047 = 'WARN', # private type alias never used
        PYI048 = 'WARN', # stub body contains multiple statements
        PYI049 = 'WARN', # private `TypedDict` never used
        PYI050 = 'CONVENTION', # prefer `Never` over `NoReturn` for function arguments
        PYI051 = 'REFACTOR', # redundant literal union
        PYI052 = 'WARN', # un-typed assignment in stub
        PYI053 = 'WARN', # string too long in stub
        PYI054 = 'WARN', # int too long in stub
        PYI055 = 'REFACTOR', # unnecessary type union
        PYI056 = 'WARN', # unsupported method call on `__all__`
        PYI057 = 'WARN', # use of `ByteString`
        PYI058 = 'REFACTOR', # use of `Generator` instead of `Iterator`
        PYI059 = 'WARN', # `Generic[]` should always be last base class

        PYI062 = 'WARN', # duplicate literal member
        PYI063 = 'WARN', # pre pip570 syntax for positional arg
        PYI064 = 'REFACTOR', # redundant final literal

        PYI066 = 'WARN', # prefer `>=` when using if-else with sys.version_info
    ),
    flake8_pytest_style = dict(
        PT001 = 'WARN', # `pytest.fixture()` used instead of `pytest.fixture`
        PT002 = 'WARN', # incorrect config for `pytest.fixture`
        PT003 = 'REFACTOR', # redundant `scope=function` in `pytest.fixture(...)`
        PT004 = None, # fixture should have leading underscore (lint deprecated)
        PT005 = None, # fixture should not have leading underscore (lint deprecated)
        PT006 = 'ERROR', # wrong type passed to first argument of `pytest.mark.parametrize`
        PT007 = 'ERROR', # wrong values passed to `pytest.mark.parametrize`
        PT008 = 'REFACTOR', # use `return_value=` instead of patching with lambda
        PT009 = 'REFACTOR', # use regular `assert` instead of unittest-style
        PT010 = 'WARN', # set expected exception in `pytest.raises`
        PT011 = 'WARN', # `pytest.raises` too broad (set match param)
        PT012 = 'WARN', # `pytest.raises` should contain a single statement
        PT013 = 'WARN', # incorrect import of pytest
        PT014 = 'WARN', # duplicate test case
        PT015 = 'WARN', # assertion always fails (replace with `pytest.fail`)
        PT016 = 'WARN', # no message passed to `pytest.fail`
        PT017 = 'WARN', # assert in `except` block (use `pytest.fail` instead)
        PT018 = 'WARN', # assertion should be broken down into multiple parts
        PT019 = 'WARN', # fixture without value is injected as param, use `pytest.mark.usefixtures`
        PT020 = 'WARN', # `pytest.yield_fixture` is deprecated
        PT021 = 'WARN', # use `yield` instead of `request.addfinalizer`
        PT022 = 'WARN', # no teardown, use `return` instead of `yield`
        PT023 = 'WARN', # incorrecet `pytest.mark` parenthesis style
        PT024 = 'WARN', # `pytest.mark.asyncio` is unnecessary for fixtures
        PT025 = 'REFACTOR', # `pytest.mark.usefixtures` has no effect on fixtures
        PT026 = 'REFACTOR', # useless `pytest.mark.usefixtures` without parameters
        PT027 = 'REFACTOR', # use `pytest.raises` instead of unittest-style
    ),
    flake8_quotes = dict(
        Q000 = None, # single quotes found but double preferred
        Q001 = None, # single quote multiline found but double preferred
        Q002 = None, # single quote docstring found but double preferred
        Q003 = 'REFACTOR', # change outer quotes to avoid escaping inner quotes
        Q004 = 'REFACTOR', # unnecessary escape on inner quote character
    ),
    flake8_raise = dict(
        RSE102 = 'REFACTOR', # unnecessary parentheses on raised exceptions
    ),
    flake8_return = dict(
        RET501 = 'CONVENTION', # do not explicitly return `None` if it's the only possible return
        RET502 = 'CONVENTION', # do not implicitly return `None` if other return values are possible
        RET503 = 'CONVENTION', # missing explicit return at end of function able to return non-`None` value
        RET504 = 'REFACTOR', # unnecessary assignment before return
        RET505 = 'REFACTOR', # unnecessary branch after return
        RET506 = 'REFACTOR', # unnecessary branch after raise
        RET507 = 'REFACTOR', # unnecessary branch after continue
        RET508 = 'REFACTOR', # unnecessary branch after break
    ),
    flake8_self = dict(
        SLF001 = 'WARN', # private member of a class accessed
    ),
    flake8_slots = dict(
        SLOT000 = 'WARN', # subclass of str should define __slots__
        SLOT001 = 'WARN', # subclass of tuple should define __slots__
        SLOT002 = 'WARN', # subclass of namedtuple should define __slots__
    ),
    flake8_simplify = dict(
        SIM101 = 'REFACTOR', # multiple `isinstance` calls can be merged
        SIM102 = 'REFACTOR', # nested `if` statements can be collapsed
        SIM103 = 'REFACTOR', # bool check can be returned directly

        SIM105 = 'REFACTOR', # use `contextlib.suppress` to supress exception

        SIM107 = 'WARN', # return in `try-except-finally`
        SIM108 = 'REFACTOR', # `if-else` can be turnery
        SIM109 = 'REFACTOR', # use `if in` instead of multiple `==` checks
        SIM110 = 'REFACTOR', # reimplementation of builtin

        SIM112 = None, # capitalize ENVVARS
        SIM113 = 'REFACTOR', # use `enumerate` for index in for loop
        SIM114 = 'REFACTOR', # multiple if branches can be combined
        SIM115 = 'REFACTOR', # use context manager for opening files
        SIM116 = 'REFACTOR', # use dictionary instead of consecutive if statements
        SIM117 = 'REFACTOR', # merge multiple `with` statements
        SIM118 = 'REFACTOR', # use `in dict` rather than `in dict.keys()``

        SIM201 = 'REFACTOR', # use `!=` instead of `not ... ==`
        SIM202 = 'REFACTOR', # use `==` instead of `not ... !=`

        SIM208 = 'REFACTOR', # expr negated twice

        SIM210 = 'REFACTOR', # unnecessary turnery
        SIM211 = 'REFACTOR', # unnecessary turnery (with not)
        SIM212 = None, # if-else checks negated expression

        SIM220 = 'REFACTOR', # unnecessary `and False`
        SIM221 = 'REFACTOR', # unnecessary `or False`
        SIM222 = 'REFACTOR', # truthy value in `or`
        SIM223 = 'REFACTOR', # falsey value in `and`

        SIM300 = 'REFACTOR', # yoda expression (constant on left side of check)

        SIM401 = 'REFACTOR', # if can be replaced with `dict.get(key, default=...)`

        SIM910 = 'REFACTOR', # if can be replaced with `dict.get(key, default=None)`
        SIM911 = 'REFACTOR', # zip can be replaced with `dict.items()`
    ),
    flake8_tidy_imports = dict(
        TID251 = 'WARN', # some import, imports a part of the api that is considered insecure and/or poor form
        TID252 = None, # prefer absolute import over relative
        TID253 = 'WARN', # import should not be done at module level due to performance issues
    ),
    flake8_type_checking = dict(
        TCH001 = 'REFACTOR', # import of local type only module outside of `TYPE_CHECKING` block
        TCH002 = 'REFACTOR', # import of third party type only module outside of `TYPE_CHECKING` block
        TCH003 = 'REFACTOR', # import of std library type only module outside of `TYPE_CHECKING` block
        TCH004 = 'ERROR',    # import of non-type only module inside of `TYPE_CHECKING`
        TCH005 = 'REFACTOR', # found empty type-checking block

        TCH010 = 'REFACTOR', # incorrect usage of typing `|` operator with quoted type annotations
    ),
    flake8_gettext = dict(
        INT001 = 'WARN', # gettext with f-string (f-string resolved before gettext)
        INT002 = 'WARN', # gettext with `.format` (`.format` resolved before gettext)
        INT003 = 'WARN', # gettext with `%` (`%` resolved before gettext)
    ),
    flake8_unused_arguments = dict(
        ARG001 = 'REFACTOR', # unused function argument
        ARG002 = 'REFACTOR', # unused method argument
        ARG003 = 'REFACTOR', # unused class method argument
        ARG004 = 'REFACTOR', # unused static method argument
        ARG005 = 'REFACTOR', # unused lambda argument
    ),
    flake8_use_pathlib = dict(
        PTH100 = None, # replace `os.path.abspath()` with `Path.resolve()`
        PTH101 = None, # replace `os.chmod()` with `Path.chmod()`
        PTH102 = None, # replace `os.mkdir()` with `Path.mkdir()`
        PTH103 = None, # replace `os.makedirs()` with `Path.mkdir(parents=True)`
        PTH104 = None, # replace `os.rename()` with `Path.rename()`
        PTH105 = None, # replace `os.rmdir()` with `Path.rmdir()`
        PTH106 = None, # replace `os.remove()` with `Path.remove()`
        PTH107 = None, # replace `os.remove()` with `Path.remove()`
        PTH108 = None, # replace `os.unlink()` with `Path.unlink()`
        PTH109 = None, # replace `os.getcwd()` with `Path.cwd()`
        PTH110 = None, # replace `os.path.exists()` with `Path.exists()`
        PTH111 = None, # replace `os.path.expanduser()` with `Path.expanduser()`
        PTH112 = None, # replace `os.path.isdir()` with `Path.is_dir()`
        PTH113 = None, # replace `os.path.isfile()` with `Path.is_file()`
        PTH114 = None, # replace `os.path.islink()` with `Path.is_symlink()`
        PTH115 = None, # replace `os.readlink()` with `Path.readlink()`
        PTH116 = None, # replace `os.stat()` with `Path.stat()`, `Path.owner()` or `Path.group()`
        PTH117 = None, # replace `os.path.isabs()` with `Path.is_absolute()`
        PTH118 = None, # replace `os.path.join()` with `Path / Path` operator
        PTH119 = None, # replace `os.path.basename()` with `Path.name`
        PTH120 = None, # replace `os.path.dirname()` with `Path.parent`
        PTH121 = None, # replace `os.path.samefile()` with `Path.samefile()`
        PTH122 = None, # replace `os.path.splitext()` with `Path.suffix`, `Path.stem` or `Path.parent`
        PTH123 = None, # replace `open` with `Path.open`
        PTH124 = 'REFACTOR', # replace `py.path` with `pathlib`

        PTH201 = 'REFACTOR', # replace `Path('.')` with `Path()`
        PTH202 = None, # replace `os.path.getsize()` with `Path.stat().st_size`
        PTH203 = None, # replace `os.path.getatime()` with `Path.stat().st_atime`
        PTH204 = None, # replace `os.path.getmtime()` with `Path.stat().st_mtime`
        PTH205 = None, # replace `os.path.getctime()` with `Path.stat().st_ctime`
        PTH206 = None, # replace `.split(os.sep)` with `Path.parts`
        PTH207 = None, # replace `glob` with `Path.glob` or `Path.rglob`
    ),
    flake8_todos = dict(
        TD001 = None, # replace XXX and FIXME with TODO
        TD002 = None, # missing author in TODO
        TD003 = None, # missing issue link in TODO
        TD004 = None, # missing colon in TODO
        TD005 = 'REFACTOR', # missing description in TODO
        TD006 = 'CONVENTION', # missing TODO capitalization 
        TD007 = 'CONVENTION', # missing space after colon in TODO
    ),
    flake8_fixme = dict(
        FIX001 = 'WARN', # line contains FIXME
        FIX002 = 'WARN', # line contains TODO
        FIX003 = 'WARN', # line contains XXX
        FIX004 = 'WARN', # line contains HACK
    ),
    eradicate = dict(
        ERA001 = 'REFACTOR', # found commented code
    ),
    pandas_vet = dict(
        PD002 = 'WARN', # `inplace=True` should be avoided (inconsistent)
        PD003 = 'REFACTOR', # `.isna` prefered over `.isnull`
        PD004 = 'REFACTOR', # `.notna` prefered over `.notnull`

        PD007 = 'REFACTOR', # `.ix` deprecated, use more explicit `.loc` or `.iloc`
        PD008 = 'REFACTOR', # use `.loc` instead of `.at`
        PD009 = 'REFACTOR', # use `.iloc` instead of `.iat`
        PD010 = 'REFACTOR', # `.pivot_table` preferred over `.pivot` or `.unstack`
        PD011 = 'REFACTOR', # use `.to_numpy()` instead of `.values`
        PD012 = 'REFACTOR', # use `.read_csv` instead of `.read_tables` to read CSV files
        PD013 = 'REFACTOR', # `.melt` prefered to `.stack`

        PD015 = 'REFACTOR', # use `.merge` method instead of `pd.merge` function

        PD101 = 'REFACTOR', # using `series.nunique()` for checking a series is constant, is ineffecient
    ),
    pygrep_hooks = dict(
        PGH001 = None, # use of `eval`, deprecated in favor of S307
        PGH002 = None, # use of `.warn` logging function, deprecated in favor if G010
        PGH003 = 'WARN', # catch-all typing ignore line
        PGH004 = 'WARN', # catch-all `noqa` used
        PGH005 = 'ERROR', # invalid `mock` usage
    ),
    pylint = dict(
        PLC0105 = 'WARN', # type name does not reeflect it's variance

        PLC0131 = 'WARN', # type cannot be both covariant and contravariant
        PLC0132 = 'WARN', # type name does not matched assigned variable name

        PLC0205 = 'WARN', # `__slots__` should be a non-string iterable
        PLC0206 = 'REFACTOR', # extracting value from dictionary without calling `.items()`

        PLC0208 = 'REFACTOR', # iterating over set literal (not effecient)

        PLC0414 = 'REFACTOR', # useless import alias
        PLC0415 = 'REFACTOR', # import outside module scope, not at top of file

        PLC1901 = 'REFACTOR', # comparison with empty string, can be changed to check if string is falsy

        PLC2401 = 'REFACTOR', # name is not ascii
        PLC2403 = 'REFACTOR', # import name is not ascii

        PLC2801 = 'WARN', # import of private name
        PLC3002 = 'REFACTOR', # unnecessary lambda call
    ),
    pylint_error = dict(
        PLE0100 = 'ERROR', # `yield` in `__init__`
        PLE0101 = 'ERROR', # `return` in `__init__`

        PLE0115 = 'ERROR', # variable is both `nonlocal` and `global` 
        PLE0116 = 'ERROR', # `continue` in `finally`
        PLE0117 = 'ERROR', # `nonlocal` without binding
        PLE0118 = 'ERROR', # name used prior to global decleration

        PLE0237 = 'ERROR', # `__slots__` is defined, but an attribute is defined that is not in the slots 

        PLE0241 = 'ERROR', # duplicate base for class 

        PLE0302 = 'ERROR', # bad special method signature
        PLE0304 = 'ERROR', # invalid `__bool__` return type
        PLE0305 = 'ERROR', # invalid `__index__` return type

        PLE0307 = 'ERROR', # invalid `__str__` return type
        PLE0308 = 'ERROR', # invalid `__bytes__` return type
        PLE0309 = 'ERROR', # invalid `__hash__` return type

        PLE0604 = 'ERROR', # invalid `__all__` (must contain only strings)
        PLE0605 = 'ERROR', # invalid type for `__all__` (must be tuple or list)

        PLE0643 = 'WARN', # likely invalid index

        PLE0704 = 'ERROR', # bare `raise` outside exception handler

        PLE1132 = 'ERROR', # repeated keyword argument

        PLE1141 = 'REFACTOR', # unppacking a dictionary in iteration without `.items()`
        PLE1142 = 'ERROR', # `await` outside of `async` function

        PLE1205 = 'ERROR', # too many arguments for logging format string
        PLE1206 = 'ERROR', # too few arguments for logging format string

        PLE1300 = 'ERROR', # bad string format character
        PLE1307 = 'ERROR', # bad string format type

        PLE1507 = 'ERROR', # invalid type for `os.getenv` argument

        PLE1519 = 'ERROR', # `@singledispatch` should not be used on methods
        PLE1520 = 'ERROR', # `@singledispatchmethod` should only be used on methods

        PLE1700 = 'ERROR', # `yield from` statement in async function

        PLE2502 = 'ERROR', # uses bidirectional unicode, which can obfuscate code

        PLE2510 = 'ERROR', # invalid unescaped character backspace (use '\b' instead)

        PLE2512 = 'ERROR', # invalid unescaped character sub (use '\x1A' instead)
        PLE2513 = 'ERROR', # invalid unescaped character esc (use '\x1B' instead)
        PLE2514 = 'ERROR', # invalid unescaped character nul (use '\0' instead)
        PLE2515 = 'ERROR', # invalid unescaped character zero-width space (use '\u200B' instead)

        PLE4703 = 'ERROR', # iterated set is modified during iteration
    ),
    pylint_refactor = dict(
        PLR0124 = 'ERROR', # name compared with itself

        PLR0133 = 'ERROR', # constant compared with another constant

        PLR0202 = 'ERROR', # classmethod defined without decorator
        PLR0203 = 'ERROR', # staticmethod defined without decorator

        PLR0206 = 'ERROR', # property has parameters

        PLR0402 = 'REFACTOR', # using `import x.y as y` instead of `from x import y`

        PLR0904 = 'REFACTOR', # too many public methods
        PLR0911 = 'REFACTOR', # too many return statements
        PLR0912 = 'REFACTOR', # too many branches
        PLR0913 = 'REFACTOR', # too many arguments
        PLR0914 = 'REFACTOR', # too many locals
        PLR0915 = 'REFACTOR', # too many statements
        PLR0916 = 'REFACTOR', # too many boolean expressions
        PLR0917 = 'REFACTOR', # too many positional arguments

        PLR1701 = None, # merge isinstance calls (deprecated in favor of SIM101)
        PLR1702 = 'REFACTOR', # too many nested blocks

        PLR1704 = 'REFACTOR', # redefined argument

        PLR1706 = None, # replace pre 2.5 ternary syntax with new, removed for false positives

        PLR1711 = 'REFACTOR', # useless return

        PLR1714 = 'REFACTOR', # repeated equality checks could be replaced with `in`

        PLR1722 = 'REFACTOR', # use of `quit` or `exit` instead of `os.exit`

        PLR1730 = 'REFACTOR', # manual reimplementation of `min` or `max`

        PLR1733 = 'REFACTOR', # unnecessary lookup of dict value by key

        PLR1736 = 'REFACTOR', # unnecessary lookup of index in enumerate loop

        PLR2004 = 'REFACTOR', # magic value used in comparison

        PLR2044 = 'REFACTOR', # empty comment

        PLR5501 = 'REFACTOR', # collapsible else if

        PLR6104 = 'REFACTOR', # non-augmented assign

        PLR6201 = None, # literal membership test doesn't use set. Disabled because this can introduce errors when members aren't hashable

        PLR6301 = 'REFACTOR', # method doesn't need to be a method
    ),
    pylint_warning = dict(
        PLW0108 = 'REFACTOR', # unnecessary lambda

        PLW0120 = 'REFACTOR', # else on loop

        PLW0127 = 'REFACTOR', # assigning var to itself
        PLW0128 = 'REFACTOR', # redeclared variable in assignment
        PLW0129 = 'WARN', # assert on string literal

        PLW0131 = 'REFACTOR', # named expression used without context

        PLW0133 = 'WARN', # exception created without raise

        PLW0177 = 'WARN', # comparing against NaN value

        PLW0211 = 'WARN', # bad staticmethod

        PLW0245 = 'WARN', # super call missing parenthesis

        PLW0406 = 'WARN', # module imports itself

        PLW0602 = 'WARN', # global variable not assigned
        PLW0603 = 'REFACTOR', # global variable updated in function
        PLW0604 = 'REFACTOR', # redundant global variable at module level

        PLW0642 = 'REFACTOR', # reassignment of `self` or `class`

        PLW0711 = 'ERROR', # catching binary operation instead of exception

        PLW1501 = 'ERROR', # bad/unknown `open` mode

        PLW1508 = 'ERROR', # invalid type for environment variable default
        PLW1509 = 'ERROR', # `preexec_fn` in `Popen`
        PLW1510 = None, # `subprocess.run` without `check` set

        PLW1514 = None, # `open` without `encoding` set

        PLW1641 = 'WARN', # object implements `__eq__` but not `__hash__`
        PLW2101 = 'ERROR', # useless `with` on `Lock`

        PLW2901 = 'REFACTOR', # variable shadowed by loop

        PLW3201 = 'REFACTOR', # bad or misspelled dunder method

        PLW3301 = 'REFACTOR', # nested `min` or `max` calls
    ),
    tryceratops = dict(
        TRY002 = 'CONVENTION', # raising vanilla exception
        TRY003 = None, # don't pass long strings to exception
        TRY004 = 'CONVENTION', # raising ValueError instead of TypeError when type is the issue

        TRY200 = None, # re-raise without cause, removed in favor of B904
        TRY201 = 'REFACTOR', # unnecessary re-raising exception with explicit name

        TRY300 = 'REFACTOR', # extra code in `try` block, should put it in an `else block`
        TRY301 = 'REFACTOR', # raise statement inside `try` block
        TRY302 = 'REFACTOR', # unnecessary immediate re-raise

        TRY400 = 'REFACTOR', # use of `logging.error` instead of `logging.exception`
        TRY401 = 'REFACTOR', # redundant exception formatted in `logger.exception` call
    ),
    flynt = dict(
        FLY002 = 'REFACTOR', # `''.join` used where f-string might be more readable
    ),
    numpy = dict(
        NPY001 = 'WARN', # deprecated type
        NPY002 = 'WARN', # legacy random, use `np.random.Generator`
        NPY003 = 'WARN', # deprecated function
        NPY201 = 'WARN', # will be deprecated in future numpy
    ),
    fastapi = dict(
        FAST001 = 'WARN', # fastapi route has redundant `response_model`
        FAST002 = 'WARN', # dependency without `Annotated`
        FAST003 = 'WARN', # parameter argument appears in route path but not in function signature
    ),
    airflow = dict(
        AIR001 = 'WARN', # task variable name should match the `task_id`
    ),
    perflint = dict(
        PERF101 = 'REFACTOR', # casting iterable to list, then iterating over it
        PERF102 = 'REFACTOR', # useless `.items()` iterator over dict

        PERF203 = 'REFACTOR', # `try-except` within a loop (performance overhead)

        PERF401 = 'REFACTOR', # `for` loop could be refactored into list comprehension
        PERF402 = 'REFACTOR', # manual list copied
        PERF403 = 'REFACTOR', # `for` loop could be refactored into dict comprehension
    ),
    refurb = dict(
        FURB101 = None, # replace `open` and `read` with `pathlib`

        FURB103 = None, # replace `open` and `write` with `pathlib`

        FURB105 = 'REFACTOR', # empty string passed to print

        FURB110 = 'REFACTOR', # ternary can be replaced with `or` operator

        FURB113 = 'REFACTOR', # repeated `.append`

        FURB116 = 'REFACTOR', # `bin`, `hex` or `oct` can be refacted to `f-string`

        FURB118 = 'REFACTOR', # manually re-implements operator

        FURB129 = 'REFACTOR', # `.readlines` instead of iterating directly over file object

        FURB131 = 'REFACTOR', # prefer `clear` of deleting slice
        FURB132 = 'REFACTOR', # use of member check + `set.remove` instead of `set.discard`

        FURB136 = 'REFACTOR', # if can be replaced with `min` or `max` calls

        FURB140 = 'REFACTOR', # use `itertools.starmap` instead of generator

        FURB142 = 'REFACTOR', # set mutation in loop that could be replaced

        FURB145 = 'REFACTOR', # prefer `.copy` over `[:]`

        FURB148 = 'REFACTOR', # `enumerate` used where iteration over length would suffice

        FURB152 = 'REFACTOR', # defined math constant used as literal

        FURB154 = 'REFACTOR', # multiple consecutive `global` or `nonlocal` keywords

        FURB157 = None, # unnecessary cast to argument of decimal constructor (disabled because this may lower precision of decimal)

        FURB161 = 'REFACTOR', # manual reimplementation of `.bit_count()`

        FURB163 = 'REFACTOR', # specifying `math.log` base instead of using specific variant
        FURB164 = 'REFACTOR', # unnecessary use of `.from_float` instead of `Decimal` or `Fraction` constructor

        FURB166 = 'REFACTOR', # use of explicit base with `int` constructor after stripping prefix
        FURB167 = 'REFACTOR', # use of regex alias
        FURB168 = 'REFACTOR', # use of `isinstance` on `None` instead of `is`
        FURB169 = 'REFACTOR', # type comparison with `None`

        FURB171 = 'REFACTOR', # membership test against single item container

        FURB177 = 'REFACTOR', # use of `Path().resolve()` instead of `Path.cwd()` for current directory

        FURB180 = 'REFACTOR', # use of `metaclass=abc.ABCMeta`
        FURB181 = 'REFACTOR', # use of hash `.digest().hex() instead of `.hexdigest()`

        FURB187 = 'REFACTOR', # assigning `reversed` instead of using `.reverse`

        FURB192 = 'REFACTOR', # use of `sorted` instead of `min` or `max`
    ),
    pydoclint = dict(
        DOC201 = 'CONVENTION', # return not documented in docstring 
        DOC202 = 'CONVENTION', # function does not return, return should not be documented in docstring

        DOC402 = 'CONVENTION', # yield is not documented in docstring
        DOC403 = 'CONVENTION', # function does not yield, yield should not be documented in docstring

        DOC501 = 'CONVENTION', # raised exception not documented in docstring
        DOC502 = 'CONVENTION', # documented raised exception not explicitly raised
    ),
    ruff = dict(
        RUF001 = 'REFACTOR', # ambiguous unicode character in string
        RUF002 = 'REFACTOR', # ambiguous unicode character in docstring
        RUF003 = 'REFACTOR', # ambiguous unicode character in comment

        RUF005 = 'REFACTOR', # literal concatenation of collection instead of spread
        RUF006 = 'ERROR', # dangling async task
        RUF007 = 'REFACTOR', # prefer `itertools.pairwise` over `zip` when iterating over successive pairs
        RUF008 = 'WARN', # mutable dataclass default value
        RUF009 = 'WARN', # function call in dataclass default
        RUF010 = 'WARN', # manual conversions inside f-string
        RUF011 = None, # static key used in dict comprehension (prefer B035 instead)
        RUF012 = 'WARN', # improperly typed mutable class variable
        RUF013 = 'WARN', # implicit optional type

        RUF015 = 'WARN', # prefer `next()` over single element slice
        RUF016 = 'WARN', # invalid index type
        RUF017 = 'WARN', # quadratic list summation
        RUF018 = 'WARN', # named expression in assert
        RUF019 = 'WARN', # unnecessary key check before dictionary access
        RUF020 = 'WARN', # never union
        RUF021 = 'WARN', # chained binary operators should be parenthesized to make precedence clear
        RUF022 = 'CONVENTION', # unsorted __all__
        RUF023 = 'CONVENTION', # unsorted __slots__
        RUF024 = 'CONVENTION', # mutable values passed to `dict.fromkeys`

        RUF026 = 'ERROR', # `default_factory` passed as kw arg to `defaultdict`
        RUF027 = 'WARN', # possible f-string missing `f` prefix
        RUF028 = 'ERROR', # suppression comment is invalid
        RUF029 = 'WARN', # async func doesn't do any async
        RUF030 = 'WARN', # print in `assert`
        RUF031 = 'WARN', # incorrect tuple subscript parenthesization
        RUF032 = 'WARN', # `Decimal()` called with float literal

        RUF100 = 'WARN', # unused `noqa` directive
        RUF101 = 'WARN', # `noqa` suppresses rule that has been deprecated in favor of another

        RUF200 = 'ERROR', # failed to parse `pyproject.toml`
    )
)

if is_in_path("ruff"):
    @register_linter
    class RuffLinter(FileLinter):
        ENABLE_TAGS: set[str] = {
            "ext:py",
            "shebang:/usr/bin/python",
            "shebang:/usr/bin/python3",
            "shebang:/usr/bin/python3.9",
        }
        DISABLE_TAGS: set[str] = set()

        def check(self, item: FileItem) -> Generator[Report, None, None]:
            for report in json.loads(
                subprocess.run(
                    ["ruff", "check", "--select=ALL", "--output-format", "json", item.abspath],
                    capture_output=True,
                    text=True,
                ).stdout
            ):
                location_metadata = ''

                level = ''
                lint_is_known = False
                for group in RUFF_LINTS.values():
                    if report['code'] in group:
                        level = group[report['code']]
                        lint_is_known = True
                        break

                if level is None:
                    # none means the lint is suppressed
                    continue

                if not lint_is_known:
                    level = 'error'

                yield FileReport(
                    item=item,
                    line=report["location"]["row"],
                    column=report["location"]["column"],
                    location_metadata=location_metadata,
                    message="[{} | {}] {}".format(
                        report["code"],
                        "?",
                        report["message"],
                    ),
                    fix=None,
                    source="ruff",
                    raw=report,
                    level=parse_report_level(level),
                )

                if not lint_is_known:
                    yield FileReport(
                        item=item,
                        line=None,
                        column=None,
                        location_metadata=None,
                        message=f"found unknown lint: {report['code']}",
                        fix=None,
                        source="ruff",
                        raw=report,
                        level=parse_report_level('error')
                    )
