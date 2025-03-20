# ruff: noqa: F401
# isort: off


def load_modules_for_ipython():
    """Load modules for use in ipython sessions and return them as a dict."""
    modules = {}
    try:
        import app.models

        modules["models"] = app.models
    except ImportError:
        log.warning("Could not import app.models")

    try:
        import app.commands

        modules["commands"] = app.commands
    except ImportError:
        log.warning("Could not import app.commands")

    return modules


# Import modules for ipython
imported_modules = load_modules_for_ipython()
globals().update(imported_modules)

import app.models
import app.commands

import funcy_pipe as fp
import sqlalchemy as sa

from activemodel.utils import find_all_sqlmodels

from playwright.async_api import async_playwright

# from activemodel import SessionManager
