import os
import sys
import re
import readline
import glob
from typing import Dict, List, Optional
from packaging.version import Version, InvalidVersion

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .tool_version_parser import ToolVersionParser
    from ...utils.path_translator import PathTranslator
    from .env_manager import CondaEnvironmentManager
except ImportError:
    from tool_version_parser import ToolVersionParser
    from utils.path_translator import PathTranslator
    from env_manager import CondaEnvironmentManager


class VersionChecker:
    """
    Integrates version checking, Conda environment selection, and dynamic UI prompts.

    This class manages:
      - Running version checks for a collection of tools.
      - Comparing installed versions against required versions.
      - Interactively prompting the user to specify environment paths when needed.
      - Displaying dynamic, color-coded output for status reporting.
    """

    COLORS = {"GREEN": "\033[92m", "RED": "\033[91m", "END": "\033[0m"}

    def __init__(self, required_tool_versions: Dict[str, str]):
        """
        Initialize the version checker.

        :param required_tool_versions: Dictionary mapping tool names to their required versions.
        """
        self.required_tool_versions = required_tool_versions
        self.tools_to_update: List[tuple] = []
        self.selected_env_paths: Dict[str, str] = {}
        self.final_tool_env_mapping: Dict[str, str] = {}
        self.installed_tool_versions: Dict[str, str] = {}
        self.path_translator = PathTranslator()
        self.env_manager = CondaEnvironmentManager()

    def _format_with_color(self, text: str, color: str) -> str:
        """
        Wrap the provided text with terminal color codes.

        :param text: The text to colorize.
        :param color: The color key (e.g., "GREEN" or "RED").
        :return: The colorized text.
        """
        return self.COLORS[color] + text + self.COLORS["END"]

    def _compare_versions(self, installed: str, required: str) -> bool:
        """
        Compare two version strings.

        Returns True if the installed version meets or exceeds the required version.

        :param installed: Installed version string.
        :param required: Required version string.
        :return: Boolean indicating if the check passes.
        """
        try:
            return Version(installed) >= Version(required)
        except InvalidVersion:
            return False

    def _queue_tool_for_update(self, tool: str, required_version: str):
        """
        Queue a tool for an update based on its version check failure.

        Some tools require custom handling for installation commands.

        :param tool: The tool name.
        :param required_version: The required version string.
        """
        if tool == "medaka":
            self.tools_to_update.append((tool, required_version, "custom"))
        elif tool == "porechop":
            display_name = "artic-porechop"
            comparison_operator = ">="
            self.tools_to_update.append(
                (display_name, required_version, comparison_operator)
            )
        elif tool in ["samtools", "bcftools"]:
            display_name = tool
            comparison_operator = "=="
            self.tools_to_update.append(
                (display_name, required_version, comparison_operator)
            )
        else:
            display_name = tool
            comparison_operator = ">="
            self.tools_to_update.append(
                (display_name, required_version, comparison_operator)
            )

    def _prompt_for_valid_path(self, prompt: str) -> str:
        """
        Prompt the user repeatedly for a valid file path with tab-completion support.

        :param prompt: The message displayed to the user.
        :return: A valid file path as entered by the user.
        """
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._complete)

        while True:
            user_input = input(f"\033[1;31m{prompt} \033[0m").strip()
            if user_input == "" or user_input == "./":
                user_input = os.getcwd()

            possible_path = os.path.join(os.getcwd(), user_input)
            if os.path.exists(possible_path):
                user_input = possible_path

            abs_path = os.path.abspath(user_input)
            if os.path.exists(abs_path):
                user_input = abs_path

            translated = self.path_translator.translate_path(user_input)
            if os.path.exists(translated):
                user_input = translated

            if user_input.isdigit():
                print("Error: A valid path cannot be a number.")
                continue

            if not os.path.exists(user_input):
                print(f"Error: {user_input} does not exist. Please enter a valid path.")
                continue

            print(f"Selected path: {user_input}")
            return user_input

    def _complete(self, text: str, state: int) -> Optional[str]:
        """
        Custom tab-completion callback for filesystem paths.

        Supports wildcard expansion for '*' or '?' characters.

        :param text: The current input text.
        :param state: The completion state.
        :return: The next possible completion, or None if no more exist.
        """
        if "*" in text or "?" in text:
            expanded = glob.glob(text)
            expanded = [
                x + ("/" if os.path.isdir(x) and not x.endswith("/") else "")
                for x in expanded
            ]
            return (expanded + [None])[state]
        else:
            directory, partial = os.path.split(text)
            if directory == "":
                directory = "."
            if not os.path.isdir(directory):
                completions = []
            else:
                completions = [
                    x for x in os.listdir(directory) if x.startswith(partial)
                ]
                completions = [
                    os.path.join(directory, x)
                    + ("/" if os.path.isdir(os.path.join(directory, x)) else "")
                    for x in completions
                ]
            return (completions + [None])[state]

    def _select_from_options(
        self, options: List[str], prompt: str, include_all: bool = False
    ) -> str:
        """
        Prompt the user to select one option from a list.

        :param options: A list of option strings.
        :param prompt: The prompt message.
        :param include_all: Whether to include an 'All' option.
        :return: The option selected by the user.
        """
        while True:
            print(prompt)
            for idx, item in enumerate(options, start=1):
                print(f"\033[1;31m{idx}.\033[0m {item}")
            if include_all:
                print(f"\033[1;31m{len(options) + 1}.\033[0m All")
            choice = input(
                f"\033[1;31mChoose an option (1-{len(options) + (1 if include_all else 0)}): \033[0m"
            ).strip()
            if not choice:
                print("Invalid entry. Please provide an option.")
                continue
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                elif include_all and choice_num == len(options) + 1:
                    return "All"
                else:
                    print(
                        "\033[1;31mInvalid choice. Please select a valid option.\033[0m"
                    )
            except ValueError:
                print("\033[1;31mInvalid input. Please enter a valid number.\033[0m")

    def _handle_version_mismatches(self):
        """
        For each tool that failed the version check, prompt the user to select or enter
        the appropriate Conda environment path.
        """
        all_envs = self.env_manager.list_conda_environments()
        for tool_name, _, _ in self.tools_to_update:
            actual_tool = "porechop" if tool_name == "artic-porechop" else tool_name
            prompt_str = (
                f"\n\033[1;31mPress Enter to select an environment for\033[0m \033[1m{tool_name}\033[0m "
                f"\033[1;31mfrom a list or enter the path now: \033[0m"
            )
            user_env_path = self._prompt_for_valid_path(prompt_str)
            if self.env_manager.is_valid_conda_environment(user_env_path):
                self.selected_env_paths[actual_tool] = user_env_path
            elif user_env_path == os.getcwd():
                print(f"\033[1;31m\nSelect the environment for {tool_name}.\033[0m")
                env_options = all_envs + ["Enter path manually"]
                selected_option = self._select_from_options(
                    env_options,
                    prompt=f"\033Available environments for {tool_name} (Choose an option):\033[0m",
                )
                if selected_option == "Enter path manually":
                    custom_env_path = self._prompt_for_valid_path(
                        f"\n\033[1;31mEnter the path for the environment containing\033[0m "
                        f"\033[1m{tool_name}\033[0m\033[1;31m:\033[0m"
                    )
                    if custom_env_path and self.env_manager.is_valid_conda_environment(
                        custom_env_path
                    ):
                        self.selected_env_paths[actual_tool] = custom_env_path
                    else:
                        print(
                            "\033[1;31mThe path entered does not exist or is not a Conda environment.\033[0m"
                        )
                else:
                    self.selected_env_paths[actual_tool] = selected_option

    def display_installation_instructions(self):
        """
        Display step-by-step instructions for installing or updating tools that failed version checks.

        The instructions include individual installation commands and an aggregated mamba command
        for convenience.
        """
        if self.tools_to_update:
            print("\nIndividual Installation Instructions:\n")
            index = 1
            for tool, version, operator in self.tools_to_update:
                if tool == "medaka" and operator == "custom":
                    print(
                        f'{index}. For medaka, run:\n  python -m pip install "medaka"'
                    )
                else:
                    print(
                        f"{index}. For {tool}, run:\n  conda install -c conda-forge -c bioconda -c gosahan "
                        f'"{tool}{operator}{version}"'
                    )
                index += 1

            non_medaka_tools = [
                f'"{t}{op}{v}"'
                for (t, v, op) in self.tools_to_update
                if not (t == "medaka" and op == "custom")
            ]
            if non_medaka_tools:
                print(
                    "\nOr install the tools using the following mamba command (excluding medaka):\n"
                )
                mamba_cmd = (
                    "mamba install -c defaults -c conda-forge -c bioconda -c gosahan "
                    + " ".join(non_medaka_tools)
                )
                print(mamba_cmd)
                print("\n")

    def check_versions(self):
        """
        Main entry point for verifying that all required tool versions are installed.

        This method iterates through each tool, executes its version command, compares the
        installed version against the required version, and interacts with the user if updates
        or environment selections are needed.
        """
        while True:
            parser = ToolVersionParser(self.selected_env_paths)
            any_failure = False
            self.tools_to_update.clear()
            print("\n\033[1mChecking program versions for NanoGO Pipeline\033[0m\n")

            # Dynamically determine the width for the tool name column.
            header_tool = "Program"
            header_version = "Version"
            header_required = "Required"
            header_pass = "Pass"
            max_tool_length = max(
                len(tool) for tool in self.required_tool_versions.keys()
            )
            header_format = (
                f"{{:<{max(max_tool_length, len(header_tool))}}} {{:<10}} {{:<10}} {{}}"
            )
            print(
                header_format.format(
                    header_tool, header_version, header_required, header_pass
                )
            )
            print("-" * (max(max_tool_length, len(header_tool)) + 30))

            for tool, required_version in self.required_tool_versions.items():
                if tool == "ivar":
                    command_str = f"{tool} version"
                elif tool == "dorado":
                    command_str = f"{tool} -vv"
                else:
                    command_str = f"{tool} --version"

                output = parser.run_version_command(tool, command_str)
                installed_version = parser.parse_tool_version(tool, output)
                if installed_version:
                    installed_version = re.sub(r"pre", "", installed_version)
                    self.installed_tool_versions[tool] = installed_version
                    passes = self._compare_versions(installed_version, required_version)
                    status_text = (
                        self._format_with_color("Pass", "GREEN")
                        if passes
                        else self._format_with_color("Fail", "RED")
                    )
                    print(
                        header_format.format(
                            tool, installed_version, required_version, status_text
                        )
                    )
                    if not passes:
                        any_failure = True
                        self._queue_tool_for_update(tool, required_version)
                else:
                    fail_text = self._format_with_color("Fail", "RED")
                    print(
                        header_format.format(
                            tool, "Not found", required_version, fail_text
                        )
                    )
                    any_failure = True
                    self._queue_tool_for_update(tool, required_version)

            if any_failure:
                self._handle_version_mismatches()
            else:
                break

        for tool in self.required_tool_versions:
            if tool in self.selected_env_paths:
                self.final_tool_env_mapping[tool] = self.selected_env_paths[tool]
            else:
                self.final_tool_env_mapping[tool] = os.environ.get("CONDA_PREFIX", "")
        print(
            "\n\033[1;31mAll required versions are nominal, NanoGO Pipeline is ready for execution.\033[0m\n"
        )

    def get_final_environment_mapping(self) -> Dict[str, str]:
        """
        Retrieve the final mapping of tool names to their associated environment paths.

        :return: Dictionary mapping tool names to environment paths.
        """
        return self.final_tool_env_mapping

    def get_installed_versions(self) -> Dict[str, str]:
        """
        Retrieve the mapping of tool names to their installed version numbers.

        :return: Dictionary mapping tool names to installed version strings.
        """
        return self.installed_tool_versions


if __name__ == "__main__":
    if __name__ == "__main__":
        required_tools = {
            # "porechop": "0.3.0",
            # "cutadapt": "4.0",
            # "medaka": "1.8.0",
            # "bcftools": "1.11",
            # "samtools": "1.11",
            # "minimap2": "2.10",
            # "qualimap": "2.2.0",
            # "fastqc": "0.11.0",
            # "NanoStat": "1.5.0",
            # "multiqc": "1.1.0",
            # "python": "3.10.0",
            # "nanogo": "0.3.0",
            # "mafft": "7.500",
            # "ivar": "1.4.2",
            # "kraken2": "2.1.0"
        }

        checker = VersionChecker(required_tools)
        checker.check_versions()
        print(checker.get_installed_versions())
        print(checker.get_final_environment_mapping())
