import re

from pylena import __version__


# From https://www.python.org/dev/peps/pep-0440/ with adjustment to pytest
def test_version():
    assert (
        re.match(
            r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$",
            __version__,
        )
        is not None
    )
