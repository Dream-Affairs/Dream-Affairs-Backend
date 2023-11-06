"""Test that all models are imported in __init__.py.""" ""
import glob
import os

from app.api import models as model_init


def test_all_models() -> None:
    """Test that all models are imported in __init__.py."""
    modules = glob.glob(
        os.path.join(os.path.dirname(model_init.__file__), "*.py")
    )
    all_models = [
        os.path.basename(f)[:-3]
        for f in modules
        if os.path.isfile(f) and not f.endswith("__init__.py")
    ]
    assert sorted(all_models) == sorted(model_init.__all__)
