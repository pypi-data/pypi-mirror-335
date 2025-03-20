"""
Path handling utilities for the NanoGO pipeline.
"""

import os
import sys
import re
import glob
import readline
import json
from pathlib import Path
from typing import List, Optional
import argparse
from .path_translator import PathTranslator


def recursive_delete(path: str) -> None:
    """
    Recursively delete a directory or file.

    Args:
        path: Path to delete
    """
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


def path_completion(text: str, state: int) -> Optional[str]:
    """
    Tab completion function for paths.

    Args:
        text: Current text to complete
        state: State of completion (which option to return)

    Returns:
        Next completion option
    """
    expanded = glob.glob(text) if "*" in text or "?" in text else []
    if expanded:
        expanded = [
            x + ("/" if os.path.isdir(x) and not x.endswith("/") else "")
            for x in expanded
        ]
        return (expanded + [None])[state]
    else:
        directory, partial = os.path.split(text)
        if directory == "":
            directory = "."
        try:
            completions = [
                os.path.join(directory, x)
                + ("/" if os.path.isdir(os.path.join(directory, x)) else "")
                for x in os.listdir(directory)
                if x.startswith(partial)
            ]
        except (PermissionError, FileNotFoundError):
            completions = []
    return (completions + [None])[state]


def path_check(prompt: str) -> str:
    """
    Check if a path exists and prompt the user for input.

    Args:
        prompt: Prompt to display to the user

    Returns:
        Validated path
    """
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(path_completion)

    while True:
        file_input_path = input(f"\033[1;31m{prompt} \033[0m").strip()

        if file_input_path == "" or file_input_path == "./":
            file_input_path = os.getcwd()

        file_input_path = (
            os.path.join(os.getcwd(), file_input_path)
            if os.path.exists(os.path.join(os.getcwd(), file_input_path))
            else file_input_path
        )
        file_input_path = (
            os.path.abspath(file_input_path)
            if os.path.exists(os.path.abspath(file_input_path))
            else file_input_path
        )
        file_input_path = (
            PathTranslator().translate_path(file_input_path)
            if os.path.exists(PathTranslator().translate_path(file_input_path))
            else file_input_path
        )

        # Check if the input is just a number, which is not a valid path
        if file_input_path.isdigit():
            print("Error: A valid path cannot be a number.")
            continue

        if not os.path.exists(file_input_path):
            print(
                f"Error: {file_input_path} does not exist. Please enter a valid path."
            )
            continue
        print(f"Selected path: {file_input_path}")
        return file_input_path


def ensure_unique_folder(folder_name: str, overwrite: bool = False) -> str:
    """
    If the folder exists, rename the existing folder by adding a unique suffix.
    Then, create a new folder with the original name.

    Args:
        folder_name: Name of the folder
        overwrite: Whether to overwrite the existing folder

    Returns:
        Path to the folder
    """
    if os.path.exists(folder_name) and not overwrite:
        suffix = 1
        new_folder_name = f"{folder_name}_{suffix}"
        while os.path.exists(new_folder_name):
            suffix += 1
            new_folder_name = f"{folder_name}_{suffix}"
        os.rename(folder_name, new_folder_name)

    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def get_valid_folder_name() -> str:
    """
    Get a valid folder name from the user.

    Returns:
        Valid folder name
    """
    while True:
        folder_name = input("Enter output folder name: ").strip()
        # Check if name is empty after stripping
        if not folder_name:
            print("Folder name cannot be empty.")
            continue
        # Check for invalid characters
        if re.search(r'[\\/:*?"<>|]', folder_name):
            print('Folder name contains invalid characters. Avoid using \\/:*?"<>|.')
            continue
        # Check for length
        if len(folder_name) > 30:
            print("Folder name is too long. Please limit it to 30 characters.")
            continue
        # Replace spaces with underscores
        folder_name = folder_name.replace(" ", "_")
        return folder_name


def is_ignored_directory(directory: Path, ignore_patterns: List[str]) -> bool:
    """Check if a directory matches any of the ignore patterns."""
    for pattern in ignore_patterns:
        if re.search(pattern, str(directory)):
            return True
    return False


def positive_float(value):
    fvalue = float(value)
    if fvalue < 0 or fvalue > 100:
        raise argparse.ArgumentTypeError(
            f"Invalid value {value}. Majority percent should be between 0 and 100."
        )
    return fvalue / 100  # Convert to decimal


def positive_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            f"Invalid value {value}. Only positive integers are allowed."
        )
    return ivalue


def process_overlap(value):
    x = int(value)
    # Check if the input value is negative and raise an error if it is
    if x < 0:
        raise argparse.ArgumentTypeError(
            f"Invalid value {value}. Value should not be negative."
        )
    overlap = int((x // 250))
    if overlap == 0:
        overlap = 1
    return overlap


def validate_cores(value):
    ivalue = int(value)
    MAX_CORES = os.cpu_count()
    if ivalue < 1 or ivalue > MAX_CORES:
        raise argparse.ArgumentTypeError(
            f"Invalid number of cores {value}. Please choose between 1 and {MAX_CORES}."
        )
    return ivalue
