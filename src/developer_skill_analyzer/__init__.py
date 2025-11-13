"""
Developer Skill Analyzer MCP Server

A Model Context Protocol server for analyzing developer skills
based on GitHub and Jira activity.
"""

__version__ = "0.1.0"
__author__ = "Victor"
__email__ = "victor@example.com"

from .server import main

__all__ = ["main"]