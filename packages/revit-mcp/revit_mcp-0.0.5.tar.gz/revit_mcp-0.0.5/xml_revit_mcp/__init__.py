"""Revit integration through the Model Context Protocol."""

__version__ = "0.0.5"

# Expose key classes and functions for easier imports
from .json_rpc import *
from .xml_revit_mcp_server import RevitConnection, get_revit_connection
