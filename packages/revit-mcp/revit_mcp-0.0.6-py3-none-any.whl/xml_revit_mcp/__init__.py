"""Revit integration through the Model Context Protocol."""

__name__ = "xml_revit_mcp"
__author__ = "zedmoster"
__version__ = "0.0.6"

# Expose key classes and functions for easier imports
from .json_rpc import *
from .xml_revit_mcp_server import RevitConnection, get_revit_connection
