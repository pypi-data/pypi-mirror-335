import os
import subprocess
from typing import List, Dict


class CondaEnvironmentManager:
    """
    Provides helper functions for managing Conda environments.

    This class offers functionality to:
      - Determine if a directory is a valid Conda environment.
      - Retrieve a list of available Conda environment paths.
      - Resolve and obtain the Conda environment for a given tool.
    """

    @staticmethod
    def is_valid_conda_environment(directory: str) -> bool:
        """
        Check if the specified directory contains a valid Conda environment.

        A valid Conda environment should have a 'conda-meta' subdirectory.

        :param directory: The directory path to validate.
        :return: True if it is a Conda environment; False otherwise.
        """
        return os.path.exists(os.path.join(directory, "conda-meta"))

    @staticmethod
    def list_conda_environments() -> List[str]:
        """
        Retrieve a list of Conda environment paths from the system.

        This method invokes 'conda env list' to parse and extract environment paths.

        :return: A list of paths corresponding to available Conda environments.
        """
        result = subprocess.run(
            ["conda", "env", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        env_paths = []
        for line in result.stdout.splitlines():
            if line and not line.startswith("#"):
                path = line.split()[-1]
                env_paths.append(path)
        return env_paths

    @staticmethod
    def get_or_prompt_conda_environment_for_tool(
        tool_name: str, tool_env_mapping: Dict[str, str], path_prompt_callback
    ) -> str:
        """
        Attempt to retrieve a conda environment path for the given tool...
        (Docstring same as above)
        """
        conda_env = tool_env_mapping.get(tool_name, os.environ.get("CONDA_PREFIX"))

        if conda_env and os.path.exists(conda_env):
            return conda_env
        else:
            print(f"\n{tool_name} not found in '{conda_env}' (or path invalid).")
            custom_env = path_prompt_callback(
                f"Please provide a path to the conda environment for {tool_name}"
            )
            return custom_env
