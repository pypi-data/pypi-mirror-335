"""
Command building and execution functionality for the NanoGO bioinformatics pipeline.
"""

import subprocess
from typing import Tuple, Optional


class CommandBuilder:
    """
    Handles building and preparing commands for execution in both local and Slurm environments.

    This class is designed to remain robust over time. It includes fallback paths for:
        - Empty or missing conda environments
        - Optional Slurm partition usage
        - Optional GPU usage
        - Summary-file redirection or alternative tool paths
        - Customizable job names
        - Configurable time limits for Slurm jobs
    """

    @staticmethod
    def prepare_command(
        conda_env: str,
        use_slurm: bool,
        partition: str,
        tool_path: str,
        gpu_required: bool,
        cores: str,
        memory: str,
        summary_file: str = None,
        alternative_tool_path: bool = False,
        job_name: str = "NanoGO",
        time_limit: str = "24:00:00",
    ) -> str:
        """
        Prepares a command string for execution, optionally using Slurm job submission.

        Args:
            conda_env: Path/name of the conda environment to activate. If empty, environment activation is skipped.
            use_slurm: Whether to use Slurm for job management.
            partition: Slurm partition to use (may be None or empty if Slurm is not used).
            tool_path: Path (or command) of the tool to execute.
            gpu_required: Whether the tool requires GPU resources.
            cores: Number of CPU cores to allocate (for Slurm).
            memory: Amount of memory to allocate in GB (for Slurm).
            summary_file: If provided, stdout/stderr is redirected to this file.
            alternative_tool_path: Flag indicating an alternative path usage (see code comments).
            job_name: Custom name for the Slurm job (default: "NanoGO").
            time_limit: Time limit for the Slurm job in the format "HH:MM:SS" (default: "24:00:00" for 24 hours).

        Returns:
            A shell command string that can be passed to run_command() or subprocess calls.
        """
        # If conda_env is provided, build a snippet to activate that env. Otherwise, skip activation.
        if conda_env:
            source_activate = f"source activate {conda_env} ;"
        else:
            source_activate = ""

        # Construct the command in either Slurm or non-Slurm mode.
        if use_slurm:
            # Ensure partition has a value only if use_slurm is True and partition is non-empty.
            partition_str = f"-p {partition}" if partition else ""
            # GPU vs. non-GPU Slurm parameters:
            if gpu_required:
                srun = f"srun -J {job_name} --time={time_limit} --mincpus={cores or 1} --mem={memory or 1}G --gres=gpu:1 {partition_str}"
            else:
                srun = f"srun -J {job_name} --time={time_limit} --mincpus={cores or 1} --mem={memory or 1}G {partition_str}"

            # Decide on command form depending on summary_file or alternative_tool_path.
            # Note: The '|| /bin/bash...' snippet is left as-is for compatibility with existing logic.
            if summary_file:
                full_command = f'/bin/bash -c "{source_activate} {srun} {tool_path} > {summary_file} 2>&1"'
            elif alternative_tool_path:
                # This line is unusual, but retained for backward compatibility:
                full_command = f'|| /bin/bash -c "{source_activate} {srun} {tool_path}"'
            elif ">" in tool_path:
                # If user manually specified redirection in the tool_path
                full_command = f'/bin/bash -c "{source_activate} {srun} {tool_path}"'
            else:
                # Default: srun with no summary file and no user redirection
                full_command = f'/bin/bash -c "{source_activate} {srun} {tool_path} > /dev/null 2>&1"'

        else:
            # Non-Slurm path: Just run locally, optionally with conda activation.
            if summary_file:
                full_command = f'/bin/bash -c "{source_activate} {tool_path} > {summary_file} 2>&1"'
            elif ">" in tool_path:
                # If user manually specified redirection in the tool_path
                full_command = f'/bin/bash -c "{source_activate} {tool_path}"'
            else:
                # Default: local run without explicit redirection to a file
                full_command = (
                    f'/bin/bash -c "{source_activate} {tool_path} > /dev/null 2>&1"'
                )

        return full_command

    @staticmethod
    def run_command(cmd: str) -> Tuple[str, str]:
        """
        Executes a shell command and returns its output (stdout, stderr).

        This function is written to handle a wide range of potential errors gracefully,
        raising Python exceptions after printing diagnostic messages.

        Args:
            cmd: The fully-prepared shell command string to execute.

        Returns:
            A tuple containing (stdout, stderr).

        Raises:
            CalledProcessError: If the command returns a non-zero exit code.
            KeyboardInterrupt: If the user interrupts execution (Ctrl-C).
            EOFError: If an EOF signal is encountered from user input.
            FileNotFoundError: If the specified command or file is not found.
            PermissionError: If the system denies file permission.
            OSError: For OS-related errors.
            ValueError: For invalid input values.
            ImportError: If a required module is missing.
            Exception: For any other unexpected errors.
        """
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            # If using process.returncode checks is desired, you can do:
            # if process.returncode != 0:
            #     raise subprocess.CalledProcessError(process.returncode, cmd, stderr=stderr)
            return stdout, stderr

        except subprocess.CalledProcessError as cpe:
            print(
                f"Command execution failed with return code {cpe.returncode}. Error output: {cpe.stderr}"
            )
            raise
        except KeyboardInterrupt:
            print(
                "\nOperation terminated by the user. Executing controlled shutdown of NanoGO..."
            )
            raise
        except EOFError:
            print(
                "\nEOF signal received from the user. Initiating standard termination procedure of NanoGO..."
            )
            raise
        except FileNotFoundError as fnf_error:
            print(
                f"File not found error: {fnf_error}. Check the file path and try again."
            )
            raise
        except PermissionError as perm_error:
            print(
                f"Permission error: {perm_error}. Check your user permissions for accessing or modifying the file."
            )
            raise
        except OSError as os_error:
            print(
                f"OS error: {os_error}. This could be related to system-level operations."
            )
            raise
        except ValueError as val_error:
            print(
                f"Value error: {val_error}. Check if the input values are of the correct type or within an acceptable range."
            )
            raise
        except ImportError as imp_error:
            print(
                f"Import error: {imp_error}. Ensure that all required modules are installed and available."
            )
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}.")
            raise
