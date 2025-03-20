"""
Environment management functionality for the NanoGO bioinformatics pipeline.
"""

import os
from typing import Dict, Optional
from os import PathLike


class EnvironmentManager:
    """Manages environment and tool paths."""

    @staticmethod
    def conda_tool(tool_name: str, tool_env_mapping: Dict[str, str]) -> str:
        """
        Gets the conda environment path for a given tool.

        Args:
            tool_name: Name of the tool
            tool_env_mapping: Mapping of tools to their conda environments

        Returns:
            Path to the conda environment
        """
        try:
            from nanogo_basecaller.utils.paths import path_check
        except ImportError:

            def path_check(prompt: str) -> str:
                """Simple fallback path check function."""
                while True:
                    file_input_path = input(f"\033[1;31m{prompt} \033[0m").strip()
                    if not os.path.exists(file_input_path):
                        print(
                            f"Error: {file_input_path} does not exist. Please enter a valid path."
                        )
                        continue
                    return file_input_path

        # Get the conda environment, with a fallback to the current conda environment
        conda_env: Optional[str] = tool_env_mapping.get(tool_name)

        # If not found in mapping, try environment variable
        if conda_env is None:
            conda_env = os.environ.get("CONDA_PREFIX", "")

        # Ensure we have a string, not None
        if not conda_env:
            conda_env = ""

        if os.path.exists(conda_env):
            return conda_env
        else:
            # Only attempt to join if conda_env is not empty
            bin_path = (
                os.path.join(conda_env, "bin") if conda_env else "undefined location"
            )
            print(f"\n{tool_name} not found in {bin_path}")
            conda_env = path_check(f"Paste path to {tool_name} conda_env: ")
            return conda_env

    @staticmethod
    def conda_version(tool_name: str, tool_version: Dict[str, str]) -> str:
        """
        Gets the version of a tool in a conda environment.

        Args:
            tool_name: Name of the tool
            tool_version: Mapping of tools to their versions

        Returns:
            Version of the tool
        """
        try:
            from nanogo_basecaller.utils.paths import path_check
        except ImportError:

            def path_check(prompt: str) -> str:
                """Simple fallback path check function."""
                while True:
                    file_input_path = input(f"\033[1;31m{prompt} \033[0m").strip()
                    if not os.path.exists(file_input_path):
                        print(
                            f"Error: {file_input_path} does not exist. Please enter a valid path."
                        )
                        continue
                    return file_input_path

        # Get the conda environment, with a fallback to the current conda environment
        conda_env: Optional[str] = tool_version.get(tool_name)

        # If not found in mapping, try environment variable
        if conda_env is None:
            conda_env = os.environ.get("CONDA_PREFIX", "")

        # Ensure we have a string, not None
        if not conda_env:
            conda_env = ""

        if os.path.exists(conda_env):
            return conda_env
        else:
            # Only attempt to join if conda_env is not empty
            bin_path = (
                os.path.join(conda_env, "bin") if conda_env else "undefined location"
            )
            print(f"\n{tool_name} not found in {bin_path}")
            conda_env = path_check(f"Paste path to {tool_name} conda_env: ")
            return conda_env

    @staticmethod
    def tool_env(
        pipeline_output_folder: str, tool_env_folder: str, delete_existing: bool = False
    ) -> str:
        """
        Creates or prepares a tool environment folder.

        Args:
            pipeline_output_folder: Base output folder
            tool_env_folder: Tool-specific folder
            delete_existing: Whether to delete existing folder contents

        Returns:
            Path to the prepared environment folder
        """
        try:
            from nanogo_basecaller.utils.paths import recursive_delete
        except ImportError:

            def recursive_delete(path: str) -> None:
                """Simple fallback recursive delete function."""
                if os.path.isdir(path):
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            recursive_delete(item_path)
                        else:
                            os.remove(item_path)
                    os.rmdir(path)
                else:
                    os.remove(path)

        output_folder = os.path.join(pipeline_output_folder, tool_env_folder)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        else:
            if delete_existing:
                recursive_delete(output_folder)
                os.makedirs(output_folder)
        return output_folder
