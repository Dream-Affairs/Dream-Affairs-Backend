"""Automatically add all models to __all__ This is used in import scripts to
import all the models in the models directory.

This is done by using the load_modules_from_path function to get all the
models in the models directory and then adding them to the __all__
variable.
"""

import glob
from os.path import abspath, basename, dirname, isfile, join, relpath


def load_modules_from_path(path):
    """Load all modules from a given path."""
    current_dir = dirname(abspath(__file__))
    absolute_path = join(current_dir, path)
    full_path = join(absolute_path, "*.py")
    modules = glob.glob(full_path)

    all_ = [
        basename(f)[:-3]
        for f in modules
        if isfile(f) and not f.endswith("__init__.py")
    ]

    return all_


# Usage
relative_path = relpath("../app/api/models", ".")
__all__ = load_modules_from_path(relative_path)
