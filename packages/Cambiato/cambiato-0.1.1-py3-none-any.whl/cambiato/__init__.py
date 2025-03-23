r"""The Cambiato package.

Cambiato is the simple yet powerful system for changing utility
devices such as district heating and electricity meters.
"""

# Local
from cambiato.app import APP_PATH
from cambiato.metadata import (
    __releasedate__,
    __version__,
    __versiontuple__,
)

# The Public API
__all__ = [
    # app
    'APP_PATH',
    # metadata
    '__releasedate__',
    '__version__',
    '__versiontuple__',
]
