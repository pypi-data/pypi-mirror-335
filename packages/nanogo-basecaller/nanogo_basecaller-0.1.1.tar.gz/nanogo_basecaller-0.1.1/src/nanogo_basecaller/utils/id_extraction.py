"""
ID extraction utilities for the NanoGO bioinformatics pipeline.

This module provides functions for extracting identifiers and other information
from files or command outputs based on string patterns.
"""

import os
import gzip
import hashlib
import subprocess
from typing import List, Optional, Union, Tuple


def extract_unique_ids(
    file_path: str = "",
    string_to_find_1: str = "",
    string_to_find_2: str = "",
    start_string_char: str = "",
    end_string_char: str = "",
    start_string_position: int = 0,
    end_string_position: int = 0,
    length_of_hash: int = 8,
    command: str = "",
    tool_env: Optional[str] = None,
    hash_generator: bool = False,
) -> List[str]:
    """
    Extract unique identifiers from a file or command output based on string patterns.

    Args:
        file_path: Path to the file or empty for command execution
        string_to_find_1: First string pattern to search for
        string_to_find_2: Second string pattern to search for
        start_string_char: Starting character/string for extraction
        end_string_char: Ending character/string for extraction
        start_string_position: Position offset from start
        end_string_position: Position offset from end
        length_of_hash: Length to truncate hash if hash_generator is True
        command: Command to execute if file_path is empty
        tool_env: Environment path for tool execution
        hash_generator: Whether to hash the extracted IDs

    Returns:
        List of unique IDs extracted
    """
    unique_id = []

    # Extract from file
    if file_path:
        try:
            open_document = gzip.open if file_path.endswith(".gz") else open
            with open_document(file_path, "rt") as f:
                for line in f:
                    if string_to_find_1 in line and string_to_find_2 in line:
                        start_index = (
                            line.find(start_string_char) + start_string_position
                        )
                        end_index = (
                            line.find(end_string_char, start_index)
                            + end_string_position
                        )
                        protocol_id = line[start_index:end_index]

                        if hash_generator and protocol_id:
                            protocol_id_hash = hashlib.sha256(
                                protocol_id.encode("utf-8")
                            ).hexdigest()[:length_of_hash]
                            if protocol_id_hash not in unique_id:
                                unique_id.append(protocol_id_hash)
                        elif protocol_id not in unique_id:
                            unique_id.append(protocol_id)
        except Exception as e:
            print(f"Error extracting from file {file_path}: {e}")

    # Extract from command output
    elif command:
        try:
            env_path = tool_env if tool_env else os.environ.get("CONDA_PREFIX", "")
            cmd = f"{env_path}/bin/{command}"
            command_exe = subprocess.run(
                [cmd],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = (
                command_exe.stdout.strip()
                if command_exe.stdout.strip()
                else command_exe.stderr.strip()
            )

            for value in output.splitlines():
                if not value:
                    continue

                # No specific string to find - process entire value
                if not string_to_find_1 and not string_to_find_2:
                    item = (
                        hashlib.sha256(value.encode("utf-8")).hexdigest()[
                            :length_of_hash
                        ]
                        if hash_generator
                        else value
                    )
                    if item not in unique_id:
                        unique_id.append(item)

                # Extract based on string patterns
                elif string_to_find_1 in value and string_to_find_2 in value:
                    start_index = value.find(string_to_find_1) + start_string_position
                    end_index = (
                        value.find(end_string_char, start_index) + end_string_position
                    )
                    extracted_id = value[start_index:end_index]

                    if hash_generator:
                        if extracted_id not in unique_id:
                            for val in extracted_id.split(" "):
                                val_hash = hashlib.sha256(
                                    val.encode("utf-8")
                                ).hexdigest()[:length_of_hash]
                                if val_hash not in unique_id:
                                    unique_id.append(val_hash)
                    elif extracted_id not in unique_id:
                        for val in extracted_id.split(" "):
                            if val not in unique_id:
                                unique_id.append(val)
        except Exception as e:
            print(f"Error executing command {command}: {e}")

    return unique_id


def hash_string(string: str, length: int = 8) -> str:
    """
    Create a hash of the input string using SHA-256.

    Args:
        string: String to hash
        length: Length to truncate the hash to

    Returns:
        Truncated hash string
    """
    return hashlib.sha256(string.encode("utf-8")).hexdigest()[:length]
