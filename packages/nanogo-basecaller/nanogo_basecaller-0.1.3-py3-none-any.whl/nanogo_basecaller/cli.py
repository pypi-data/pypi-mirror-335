#!/usr/bin/env python3
"""
Command-line interface for NanoGO bioinformatics pipeline.

This module provides the main entry point for the NanoGO command line tool,
which offers subcommands for basecalling, analysis, and other functionalities.
It automatically uses the latest available Dorado version or falls back to a
default version if needed.
"""

import sys
import argparse
from typing import List, Optional
import os
import subprocess
import re
import shutil
from .workflows.basecalling import BasecallingWorkflow


def get_dorado_version() -> str:
    """
    Get the installed Dorado version.

    Returns:
        String representing the Dorado version or "not found" if Dorado is not installed
    """
    dorado_bin = shutil.which("dorado")
    if not dorado_bin:
        return "not found"

    try:
        result = subprocess.run(
            [dorado_bin, "--version"], capture_output=True, text=True, check=True
        )
        version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
        if version_match:
            return version_match.group(1)
        return "unknown"
    except (subprocess.SubprocessError, OSError):
        return "error checking version"


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for NanoGO.

    Returns:
        Configured ArgumentParser instance
    """
    dorado_version = get_dorado_version()

    parser = argparse.ArgumentParser(
        prog="nanogo",
        description="NanoGO Basecaller: A comprehensive bioinformatics pipeline for Oxford Nanopore Technologies. "
        "The tool offers Dorado-based basecalling with duplex options, amplicon read assembly and polishing, "
        "primer trimming, and quality control. Designed for efficient parallel processing and enhanced by interactive "
        "input and output configuration, NanoGO maximizes computational resources while providing flexible control to users.\n\n"
        f"Current Dorado version: {dorado_version}",
        epilog=(
            "\033[1m\033[31mCopyright:\033[0m \033[1mGovernment of Canada\033[0m\n"
            "\033[1m\033[31mWritten by:\033[0m \033[1mNational Microbiology Laboratory, Public Health Agency of Canada\033[0m"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        usage="%(prog)s [options] <subcommand>",
    )

    # Version argument available at top level
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.3",
        help="Display the version number of NanoGO.",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        title="Available Tools",
        description="Valid subcommands",
        help="Description",
        dest="command",
        required=False,  # Changed to False to allow running with no command
    )

    # Add basecaller command
    add_basecaller_parser(subparsers, dorado_version)

    return parser


def add_basecaller_parser(subparsers, dorado_version: str) -> None:
    """
    Add the basecaller command parser to the subparsers.

    Args:
        subparsers: Subparsers object to add the basecaller parser to
        dorado_version: Current Dorado version string
    """
    parser_basecaller = subparsers.add_parser(
        "basecaller",
        help="Run nanogo basecaller using the latest available Dorado version",
        usage="nanogo basecaller -i <raw_ont-data_folder> -o <output_directory_name> [Basecaller Options]",
        epilog=f"Using Dorado version: {dorado_version}\n"
        "The basecaller automatically uses the latest available Dorado version and falls back to a default version if needed.\n"
        "This ensures your analysis benefits from the most recent improvements in basecalling technology.",
    )

    # Main options
    dorado_basecaller = parser_basecaller.add_argument_group("Main Options")
    dorado_basecaller.add_argument(
        "-i",
        dest="input",
        metavar="<raw_ont-data_folder>",
        help="Path to the folder containing raw ONT data. If not provided, the program enters interactive mode.",
        required=False,
    )
    dorado_basecaller.add_argument(
        "-o",
        dest="output",
        metavar="<output_directory_name>",
        help='Output directory where results will be stored. Defaults to "dorado_output" within the input directory.',
        default="dorado_output",
        required=False,
    )

    # Basecaller-specific options
    dorado_basecaller_models = parser_basecaller.add_argument_group(
        "Basecaller Options"
    )
    dorado_basecaller_models.add_argument(
        "-b",
        "--basecaller",
        dest="basecaller",
        action="store_true",
        help="Enable to specify and use a particular basecalling software. Enabled by default.",
        required=False,
        default=True,
    )
    dorado_basecaller_models.add_argument(
        "-d",
        "--duplex",
        dest="duplex",
        action="store_true",
        help="Enable for duplex sequencing mode, which processes both DNA strands. Not enabled by default.",
        required=False,
        default=False,
    )
    dorado_basecaller_models.add_argument(
        "--ignore",
        dest="ignore_patterns",
        action="append",
        metavar="<ignore_pattern>",
        help="Ignore files matching the provided pattern.",
        required=False,
    )

    # Add model selection options
    dorado_basecaller_models.add_argument(
        "-m",
        "--model",
        dest="model",
        metavar="<model_name>",
        help="Specify a particular Dorado model to use for basecalling. If not specified, the default model will be used.",
        required=False,
    )

    # Add device options
    dorado_device = parser_basecaller.add_argument_group("Device Options")
    dorado_device.add_argument(
        "--device",
        dest="device",
        choices=["auto", "cpu", "gpu"],
        default="auto",
        help="Specify the computing device to use: 'auto' (default, uses GPU if available), 'cpu', or 'gpu'.",
    )
    dorado_device.add_argument(
        "--gpu-device",
        dest="gpu_device",
        type=int,
        metavar="<device_id>",
        help="Specify the GPU device ID to use (default: 0).",
        default=0,
    )

    # Add advanced options
    dorado_advanced = parser_basecaller.add_argument_group("Advanced Options")
    dorado_advanced.add_argument(
        "--check-version",
        dest="check_version",
        action="store_true",
        help="Check for the latest Dorado version before running basecalling (default: enabled).",
        default=True,
    )
    dorado_advanced.add_argument(
        "--threads",
        dest="threads",
        type=int,
        metavar="<num_threads>",
        help="Number of threads to use for basecalling (default: auto).",
    )
    dorado_advanced.add_argument(
        "--chunk-size",
        dest="chunk_size",
        type=int,
        metavar="<chunk_size>",
        help="Chunk size for processing (default: determined by Dorado).",
    )
    dorado_advanced.add_argument(
        "--modified-bases",
        dest="modified_bases",
        action="store_true",
        help="Enable modified base detection (requires compatible model).",
        default=False,
    )

    # Version argument for basecaller
    parser_basecaller.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.3",
        help="Display the version number of NanoGO.",
    )


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the NanoGO command-line interface.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()

    # If no arguments were provided, print help and exit
    if args is None:
        args = sys.argv[1:]

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # If no command is provided or command is not 'basecaller', show help and exit
    if not parsed_args.command:
        parser.print_help(sys.stderr)
        return 0

    # Only proceed if the command is 'basecaller'
    if parsed_args.command != "basecaller":
        print(f"The '{parsed_args.command}' command is not currently implemented.")
        print("Please use 'nanogo basecaller' to run the basecaller.")
        return 1

    try:
        workflow = BasecallingWorkflow(parsed_args)
        return workflow.run()
    except KeyboardInterrupt:
        print("\nOperation terminated. Executing controlled shutdown of NanoGO...")
        return 130  # Standard exit code for SIGINT
    except EOFError:
        print(
            "\nEOF signal received. Initiating standard termination procedure of NanoGO..."
        )
        return 1
    except FileNotFoundError as e:
        print(f"File not found error: {e}. Check the file path and try again.")
        return 1
    except PermissionError as e:
        print(
            f"Permission error: {e}. Check your user permissions for accessing or modifying the file."
        )
        return 1
    except OSError as e:
        print(f"OS error: {e}. This could be related to system-level operations.")
        return 1
    except ValueError as e:
        print(
            f"Value error: {e}. Check if the input values are of correct type or within an acceptable range."
        )
        return 1
    except ImportError as e:
        print(
            f"Import error: {e}. Ensure that all required modules are installed and available."
        )
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
