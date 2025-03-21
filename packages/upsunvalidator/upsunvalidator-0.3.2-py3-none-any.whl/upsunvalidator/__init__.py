"""Validation library for Upsun Configuration."""

try:
    from upsunvalidator._version import version as __version__
except ImportError:
    __version__ = "0.0.0.dev0"  # Fallback version if not installed from git

# Bring most important methods into main namespace for MCP tools.
from upsunvalidator.validate.validate import validate, validate_string
from upsunvalidator.examples import (
    get_available_example_names,
    get_example_config,
    get_example_config_with_info,
)
