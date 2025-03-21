# Pylena image processing library

[![image alt pipeline](https://gitlab.lre.epita.fr/olena/pylena/badges/master/pipeline.svg)](https://gitlab.lre.epita.fr/olena/pylena/-/commits/master)
[![image alt python coverage](https://gitlab.lre.epita.fr/olena/pylena/badges/master/coverage.svg?job=python_coverage&key_text=Python+Coverage&key_width=100)](https://gitlab.lre.epita.fr/olena/pylena/-/commits/master)
[![image alt cpp coverage](https://gitlab.lre.epita.fr/olena/pylena/badges/master/coverage.svg?job=cpp_coverage&key_text=C%2B%2B+Coverage&key_width=100)](https://gitlab.lre.epita.fr/olena/pylena/-/commits/master)

Pylena is the Python interface to the modern C++ image processing library
[Pylene](https://gitlab.lre.epita.fr/olena/pylene). Its aim is to fill the three following requirements:
* Interactivity
* Genericity
* Efficiency

Many image processing libraries succeed to fill these requirements but they are
still limited by the static nature of the C++ language, where the genericity,
based on *templates*, is resolved at compile time. Thus, the goal of this library is to tackle this problem.

## Supported Python version

Currently, Pylena is tested and provides wheel for the following Python version:

* CPython 3.9
* CPython 3.10
* CPython 3.11
* CPython 3.12
* CPython 3.13

## Installation

Pylena is available on the [PyPI](https://pypi.org/) server and can be simply
installed with [pip](https://pip.pypa.io/en/stable/) by executing the following
command:

```
$ pip install pylena
```

## Documentation

The documentation is available [here](http://olena.pages.lre.epita.fr/pylena/).

## Contributing

If you find any bug or have any suggestions, feel free to create a new issue
[here](https://gitlab.lre.epita.fr/olena/pylena/-/issues) or send an email to
[baptiste.esteban@epita.fr](mailto:baptiste.esteban@epita.fr).

## Licence

[Mozilla Public License Version 2.0](https://www.mozilla.org/en-US/MPL/2.0/)
