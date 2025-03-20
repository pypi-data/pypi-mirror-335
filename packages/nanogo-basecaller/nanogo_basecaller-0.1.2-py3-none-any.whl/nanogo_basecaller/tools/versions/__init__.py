"""
NanoGO Versions Tool Implementation for the NanoGO bioinformatics pipeline.

This package provides a robust interface for checking tool versions and managing
their associated Conda environments. It includes modules to execute version commands,
parse tool output, translate file paths between Windows and Linux, and interactively
select or prompt for Conda environments.

Modules:
    - exceptions: Custom exceptions for handling version check failures.
    - tool_version_parser: Functionality to execute version commands and parse output.
    - path_translator: Tools for converting Windows-style paths to Linux-compatible paths.
    - env_manager: Management and interaction with Conda environments.
    - version_checker: Integration of version checking, environment selection, and UI prompts.

:author: Gurasis Osahan
:version: 0.1.0
"""

from .env_manager import *
from .exceptions import *
from .tool_version_parser import *
from .version_checker import *
