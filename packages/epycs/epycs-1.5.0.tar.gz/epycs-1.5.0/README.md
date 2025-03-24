# Epycs

Epycs is a simple way to convert shell scripts to python.
It features

  - A simple subprocess API
  - A sane behaviour of exiting by default on subprocess failures
  - A show-output-on-fail behaviour

The goal of this package is to be able to write shell-script equivalent code
in python while still being terse, but adding a tons of goodness in terms of
arithmetical expression, string manipulation, code reuse etc...

Say no to .sh and welcome .py with epycs, you'll thank me later.

# Changelog

* v1.5.0

`epycs.cmd` directly accessible

`ShellProgram.add` supports kwargs, deprecated other methods, they will be removed
in a future version.

`ShellProgram.env(name=value)` for setting additional environment variables

tox testing on python 3.7 to 3.13

Various CI fixes

Using UV for package management

* v1.4.0

Improved handling of additional environment (allows any str-convertible,
and providing `None` deletes the env var)

Added new `python_to_subprocess` function, which turns a local python
function to a full-fledged subprocess, allowing for pure-python piping.

* v1.3.0

Added sourcing of shell scripts

Added new `out_filter=text_lines_0` that splits by NUL character

* v1.2.0

Added epycs.config for lightweight user-defined config management
