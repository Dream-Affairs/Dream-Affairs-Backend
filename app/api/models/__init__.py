"""Automatically add all models to __all__ This is used in alembic while
autogenerating database migration script."""

import glob
from os.path import basename, dirname, isfile, join

modules = glob.glob(join(dirname(__file__), "*.py"))

__all__ = [
    basename(f)[:-3]
    for f in modules
    if isfile(f) and not f.endswith("__init__.py")
]
