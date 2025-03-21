import os

def _get_version():
    with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
        return f.read().strip()

__version__ = _get_version()