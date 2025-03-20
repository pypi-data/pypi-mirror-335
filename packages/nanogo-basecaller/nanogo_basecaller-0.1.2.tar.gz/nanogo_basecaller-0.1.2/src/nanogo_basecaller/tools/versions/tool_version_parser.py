import os
import re
import subprocess
from typing import Dict, List, Optional


class ToolVersionParser:
    """
    Executes version commands for tools and parses their output to extract version numbers.

    This class handles both primary and fallback methods to determine the installed version
    of a given tool by running subprocess commands.
    """

    def __init__(self, tool_environment_paths: Dict[str, str]):
        """
        Initialize the parser with a mapping from tool names to their associated environment paths.

        :param tool_environment_paths: Dictionary mapping tool names to Conda environment paths.
        """
        self.tool_environment_paths = tool_environment_paths

    def run_version_command(self, tool: str, command: str) -> str:
        """
        Execute the version command for a tool and return the combined output.

        The method attempts to run the primary command (using the tool's binary path) and,
        if that fails, falls back to a pip command to show version details.

        :param tool: The name of the tool.
        :param command: The version command string (e.g., "samtools --version").
        :return: The stdout or stderr output from the command execution.
        """
        command_list = command.split()
        env_path = os.environ.get("CONDA_PREFIX", "")
        if tool in self.tool_environment_paths:
            env_path = self.tool_environment_paths[tool]

        primary_cmd_path = os.path.join(env_path, "bin", command_list[0])
        primary_command = [primary_cmd_path] + command_list[1:]

        def _attempt_run(
            cmd: List[str], use_shell: bool = False
        ) -> subprocess.CompletedProcess:
            return subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=use_shell,
                check=False,
            )

        if os.path.exists(primary_cmd_path):
            primary_result = _attempt_run(primary_command)
            if primary_result.returncode != 0:
                fallback_str = (
                    f"{os.path.join(env_path, 'bin', command_list[0])} --version || "
                    f"{os.path.join(env_path, 'bin', 'pip')} show -v {tool}"
                )
                fallback_result = _attempt_run([fallback_str], use_shell=True)
                return fallback_result.stdout.strip() or fallback_result.stderr.strip()
            else:
                return primary_result.stdout.strip() or primary_result.stderr.strip()
        else:
            fallback_str = (
                f"{primary_cmd_path} --version || "
                f"{os.path.join(env_path, 'bin', 'pip')} show -v {tool}"
            )
            fallback_result = _attempt_run([fallback_str], use_shell=True)
            return fallback_result.stdout.strip() or fallback_result.stderr.strip()

    def parse_tool_version(self, tool: str, output: str) -> Optional[str]:
        """
        Extract the version number from the output of a tool's version command.

        This method applies specific regular expressions for known tools, falling back to
        generic patterns if necessary.

        :param tool: The tool's name.
        :param output: The raw output from the version command.
        :return: The extracted version number, or None if parsing fails.
        """
        if re.search(
            r"(not found|No such file or directory|CommandNotFoundError|not recognized)",
            output,
            re.IGNORECASE,
        ):
            return None

        # Special cases for tools with non-standard version outputs.
        if tool == "quasigo":
            match = re.search(r"version\s([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "qualimap":
            match = re.search(r"v\.([\d\.]+)-dev", output, re.IGNORECASE)
            if match:
                return match.group(1)
            match = re.search(r"v\.([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "porechop":
            match = re.search(r"([\d\.]+pre)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "minimap2":
            match = re.search(r"([\d\.]+)-r\d+", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "cutadapt":
            match = re.search(r"([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "multiqc":
            match = re.search(r"version (\d+\.\d+)", output)
            return match.group(1) if match else None
        elif tool == "mafft":
            match = re.search(r"v(\d+\.\d+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "kraken2":
            match = re.search(r"version\s([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "ivar":
            match = re.search(r"version\s([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "dorado":
            match = re.search(r"dorado:\s*([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None
        elif tool == "pod5":
            match = re.search(r"Pod5 version:\s*([\d\.]+)", output, re.IGNORECASE)
            return match.group(1) if match else None

        # General fallback patterns.
        pattern = re.compile(rf"{tool}\s+([\d\.]+)", re.IGNORECASE)
        match = pattern.search(output)
        if match:
            return match.group(1)

        match = re.search(r"(\d[\d\.]*)", output)
        if match:
            return match.group(1)

        return None
