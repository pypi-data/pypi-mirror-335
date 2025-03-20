"""
Workflow for Oxford Nanopore basecalling using Dorado.

This module provides a workflow for basecalling ONT data using the Dorado basecaller,
with support for duplex basecalling and multi-GPU processing.
"""

import os
import sys
import time
from typing import Optional, Union, List, Dict, Any, Tuple

# Ensure parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nanogo_basecaller.tools.basecaller.dorado import DoradoBasecaller
    from nanogo_basecaller.tools.versions.version_checker import VersionChecker
    from nanogo_basecaller.core.slurm import SlurmManager
    from nanogo_basecaller.utils.io_selection import (
        interactivate_nanogo_input,
        interactivate_output_path,
    )
except ImportError:
    from tools.basecaller.dorado import DoradoBasecaller
    from tools.versions.version_checker import VersionChecker
    from core.slurm import SlurmManager
    from utils.io_selection import interactivate_nanogo_input, interactivate_output_path


class BasecallingWorkflow:
    """
    Workflow for basecalling Oxford Nanopore data using Dorado.

    This workflow handles the end-to-end process of basecalling, including:
    1. Version checking for required tools
    2. Input and output path selection (interactive or from arguments)
    3. GPU/processing chunk configuration
    4. Basecalling execution with or without duplex mode
    5. Output file renaming and organization
    """

    def __init__(self, args):
        """
        Initialize the basecalling workflow with command-line arguments.

        Args:
            args: Parsed command-line arguments
        """
        self.args = args
        self.basecaller = DoradoBasecaller()
        self.version_checker = VersionChecker({"dorado": "0.6.0", "pod5": "0.3.10"})

    def run(self) -> int:
        """
        Execute the complete basecalling workflow.

        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        try:
            # Check versions of required tools
            tool_versions, tool_env_mapping = self._check_versions()

            # Handle input and output path selection
            input_folder, output_folder = self._setup_io_paths()

            # Configure SLURM and determine resources
            slurm_status, partition = self._setup_slurm()
            num_gpus = self._get_num_gpus(slurm_status)

            # Run basecalling process
            self._run_basecalling(
                slurm_status,
                partition,
                input_folder,
                output_folder,
                num_gpus,
                tool_env_mapping,
            )

            print("\033[1;32mBasecalling workflow completed successfully.\033[0m")
            return 0

        except KeyboardInterrupt:
            print("\n\033[1;31mWorkflow interrupted by user. Exiting...\033[0m")
            return 130
        except Exception as e:
            print(f"\033[1;31mError in basecalling workflow: {e}\033[0m")
            import traceback

            traceback.print_exc()
            return 1

    def _check_versions(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Check versions of required tools.

        Returns:
            Tuple of (tool_versions, tool_env_mapping)
        """
        try:
            # Check if the version control works
            self.version_checker.check_versions()
            return (
                self.version_checker.get_installed_versions(),
                self.version_checker.get_final_environment_mapping(),
            )
        except Exception as e:
            print(f"\033[1;31mError checking tool versions: {e}\033[0m")
            raise

    def _setup_io_paths(self) -> Tuple[Union[str, List[str]], Union[str, List[str]]]:
        """
        Set up input and output paths, either from arguments or interactively.

        Returns:
            Tuple of (input_folder, output_folder)
        """
        # Process ignore patterns
        user_ignore_patterns = (
            self.args.ignore_patterns
            if hasattr(self.args, "ignore_patterns")
            and self.args.ignore_patterns is not None
            else []
        )

        # Handle input selection
        if not hasattr(self.args, "input") or self.args.input is None:
            input_folder = interactivate_nanogo_input(
                provided_path=None,
                ignore_patterns=user_ignore_patterns,
                file_type="basecaller",
            )
        else:
            input_folder = interactivate_nanogo_input(
                provided_path=self.args.input,
                ignore_patterns=user_ignore_patterns,
                file_type="basecaller",
            )

        # Handle output folder
        output_name = (
            self.args.output if hasattr(self.args, "output") else "dorado_output"
        )
        output_folder = interactivate_output_path(input_folder, output_name)

        return input_folder, output_folder

    def _setup_slurm(self) -> Tuple[bool, Optional[str]]:
        """
        Set up SLURM if available and selected by user.

        Returns:
            Tuple of (slurm_status, partition)
        """
        return SlurmManager.slurm_selection()

    def _get_num_gpus(self, slurm_status: bool) -> int:
        """
        Interactively determine the number of GPUs or processing chunks to use.

        Args:
            slurm_status: Whether running in SLURM environment

        Returns:
            Number of GPUs or processing chunks to use
        """
        prompt = (
            "Enter the number of GPUs to use for basecalling: "
            if slurm_status
            else "Enter the number of chunks to divide your data into for basecalling: "
        )
        error_msg = (
            "Error: Please enter a positive number of GPUs to use for basecalling."
            if slurm_status
            else "Error: Please enter a valid number of chunks to divide your data into for basecalling."
        )

        while True:
            try:
                num = int(input(prompt))
                if num < 1 or num > 100:
                    print(error_msg)
                else:
                    return num
            except ValueError:
                print("Error: Please enter a valid integer number.")

    def _run_basecalling(
        self,
        slurm_status: bool,
        partition: Optional[str],
        input_folder: Union[str, List[str]],
        output_folder: Union[str, List[str]],
        num_gpus: int,
        tool_env_mapping: Dict[str, str],
    ) -> None:
        """
        Run the basecalling process.

        Args:
            slurm_status: Whether to use SLURM
            partition: SLURM partition to use
            input_folder: Input folder(s)
            output_folder: Output folder(s)
            num_gpus: Number of GPUs or processing chunks
            tool_env_mapping: Tool environment mapping
        """
        print("\033[1;34mPreparing data for basecalling...\033[0m")
        results = self.basecaller.prepare_data(
            slurm_status,
            partition,
            input_folder,
            num_gpus,
            output_folder,
            tool_env_mapping,
        )

        # Determine if using duplex mode
        duplex_mode = self.args.duplex if hasattr(self.args, "duplex") else False
        mode_str = "duplex" if duplex_mode else "standard"
        print(f"\033[1;34mRunning {mode_str} basecalling...\033[0m")

        # Run basecalling
        self.basecaller.run_basecalling(
            slurm_status, partition, tool_env_mapping, results, duplex_mode=duplex_mode
        )

        # Allow time for file operations to complete
        print("\033[1;34mFinalizing basecalling outputs...\033[0m")
        time.sleep(5)

        # Rename and organize output files
        self.basecaller.rename_files(results)


def run_basecalling_workflow(args) -> int:
    """
    Run the basecalling workflow with the given arguments.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    workflow = BasecallingWorkflow(args)
    return workflow.run()
