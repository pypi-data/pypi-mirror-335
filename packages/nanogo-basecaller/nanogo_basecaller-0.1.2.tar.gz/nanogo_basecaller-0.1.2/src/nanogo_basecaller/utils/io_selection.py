"""
Interactive I/O selection utilities for the NanoGO bioinformatics pipeline.
"""

import os
import sys
import glob
import subprocess
from pathlib import Path
from typing import List, Union, Tuple, Optional
from .paths import (
    path_check,
    is_ignored_directory,
    get_valid_folder_name,
    ensure_unique_folder,
)
from .cli_select import select_option
from .file_finder import find_files_by_pattern


# Global variable to track if all input folders were selected
all_input_selected = False

# Rest of the file remains the same


class InputSelector:
    """Class for handling interactive file input selection."""

    def __init__(self, file_type="analysis"):
        """
        Initialize the input selector.

        Args:
            file_type: Type of files to look for ('analysis' for FASTQ, 'basecaller' for FAST5/POD5)
        """

        self.path_check = path_check
        self.is_ignored_directory = is_ignored_directory
        self.select_option = select_option
        self.find_files_by_pattern = find_files_by_pattern

        # Define default patterns to ignore for each file type
        self.default_patterns = {
            "analysis": [
                r"nanogo_output_\d+",
                "temp_data",
                r"sublist_\d+",
                "adapter_trimmed_reads",
                "consensus_alignments",
                "final_consensus",
                "primer_trimmer_reads",
                "quality_control",
                "nanogo_output",
            ],
            "basecaller": [r"temp_data", r"sublist_\d+"],
        }

        # Define file extensions for each file type
        self.file_extensions = {
            "analysis": [".fastq", ".fastq.gz"],
            "basecaller": [".fast5", ".pod5"],
        }

        self.file_type = file_type

    def find_relevant_files(
        self, base_path: str, ignore_patterns: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Find files with specific extensions in a directory."""
        relevant_files = []

        # Convert extensions to patterns
        file_patterns = [
            f"*{ext}" for ext in self.file_extensions.get(self.file_type, [])
        ]

        # Find all matching files
        for pattern in file_patterns:
            matching_files = self.find_files_by_pattern(
                base_path, [pattern], ignore_patterns
            )
            relevant_files.extend(matching_files)

        # If no files found, prompt user for another directory
        if not relevant_files:
            file_ext_str = ", ".join(self.file_extensions.get(self.file_type, []))
            print(f"No {file_ext_str} files found in the directory")

            valid_input = False
            while not valid_input:
                prompt_text = {
                    "analysis": "Enter path to base folder containing demultiplexed & basecalled data: ",
                    "basecaller": "Enter path to base folder containing raw ONT data: ",
                }
                input_main_dir = self.path_check(
                    f'\n{prompt_text.get(self.file_type, "")}'
                )

                # Try again with the new directory
                for pattern in file_patterns:
                    matching_files = self.find_files_by_pattern(
                        input_main_dir, [pattern], ignore_patterns
                    )
                    if matching_files:
                        relevant_files.extend(matching_files)
                        valid_input = True

        # Extract unique parent directories
        relevant_folders = list(set(os.path.dirname(file) for file in relevant_files))

        return relevant_files, relevant_folders

    def select_input_folder(self, relevant_folders: List[str]) -> Union[List[str], str]:
        """Present a list of folders to the user and get their selection."""
        global all_input_selected

        prompt_text = {
            "analysis": "Select the folder to run NanoGO Analysis Pipeline on:",
            "basecaller": "Select the folder to run NanoGO Basecaller Pipeline on:",
        }

        # Add option to choose another folder
        input_folder = self.select_option(
            sorted(relevant_folders) + ["Choose another folder"],
            prompt_text.get(self.file_type, "Select folder:"),
            include_all=True,
        )

        if input_folder == "Choose another folder":
            prompt_text = {
                "analysis": "Enter path to base folder containing demultiplexed & basecalled data: ",
                "basecaller": "Enter path to base folder containing raw ONT data: ",
            }
            input_main_dir = self.path_check(f'\n{prompt_text.get(self.file_type, "")}')
            _, new_folders = self.find_relevant_files(input_main_dir, [])
            return self.select_input_folder(new_folders)

        if input_folder == "All":
            all_input_selected = True
            return sorted(relevant_folders)
        else:
            all_input_selected = False
            return [input_folder]

    def interactive_selection(
        self, provided_path: Optional[str] = None, ignore_patterns: List[str] = []
    ) -> List[str]:
        """Find and select input folders for NanoGO interactively."""
        # Combine default and user-provided patterns
        all_ignore_patterns = (
            self.default_patterns.get(self.file_type, []) + ignore_patterns
        )

        # Process provided path if given
        if provided_path:
            # Try different path variants
            for path_variant in [
                provided_path,
                os.path.join(os.getcwd(), provided_path),
                os.path.abspath(provided_path),
            ]:
                if os.path.exists(path_variant):
                    provided_path = path_variant
                    break

            # If it's a file, use its parent directory
            if os.path.isfile(provided_path):
                file_ext = "".join(Path(provided_path).suffixes)
                if file_ext in self.file_extensions.get(self.file_type, []):
                    return [os.path.dirname(provided_path)]
                else:
                    raise ValueError(
                        f"The provided file {provided_path} is not a supported file type."
                    )

            # If it's a directory, find relevant files
            elif os.path.isdir(provided_path):
                _, relevant_folders = self.find_relevant_files(
                    provided_path, all_ignore_patterns
                )

                if not relevant_folders:
                    raise ValueError(f"No relevant files found in {provided_path}.")

                return self.select_input_folder(relevant_folders)

            # If path doesn't exist
            else:
                raise ValueError(f"The provided path {provided_path} does not exist.")

        # No path provided, prompt user interactively
        else:
            prompt_text = {
                "analysis": "Enter path to base folder containing demultiplexed & basecalled data: ",
                "basecaller": "Enter path to base folder containing raw ONT data: ",
            }

            input_main_dir = self.path_check(f'\n{prompt_text.get(self.file_type, "")}')

            _, relevant_folders = self.find_relevant_files(
                input_main_dir, all_ignore_patterns
            )

            if not relevant_folders:
                raise ValueError(f"No relevant files found in {input_main_dir}.")

            return self.select_input_folder(relevant_folders)


def interactivate_nanogo_input(
    provided_path: Optional[str] = None,
    ignore_patterns: List[str] = [],
    file_type: str = "analysis",
) -> List[str]:
    """
    Find and select input folders for NanoGO interactively.

    Args:
        provided_path: Path provided as an argument, if any
        ignore_patterns: List of directory patterns to ignore
        file_type: Type of files to look for ('analysis' for FASTQ, 'basecaller' for FAST5/POD5)

    Returns:
        List of selected input folders
    """
    selector = InputSelector(file_type)
    return selector.interactive_selection(provided_path, ignore_patterns)


def interactivate_file_selection(
    input_folders: Union[str, List[str]],
    file_extension: str,
    prompt: str,
    provided_path: Optional[str] = None,
) -> Union[str, List[str]]:
    """
    Interactively select files from input folders.

    Args:
        input_folders: Input folder(s) to search in
        file_extension: File extension to look for (e.g., '.txt', '.fasta')
        prompt: Prompt to display when selecting files
        provided_path: Path provided as an argument, if any

    Returns:
        Selected file path(s)
    """

    all_input_selected = isinstance(input_folders, list) and len(input_folders) > 1

    def loop_check(folder=""):
        valid_input = False
        while not valid_input:
            input_main_dir = path_check(
                f'\nEnter path to folder containing {file_extension} file{" " + folder if folder else ""}: '
            )
            matching_files = glob.glob(
                os.path.join(input_main_dir, f"*{file_extension}"), recursive=False
            )

            if matching_files:
                file_path = select_option(
                    matching_files + ["Choose another folder"],
                    f"Select a {file_extension} file to run NanoGO Pipeline on:",
                )
                if file_path == "Choose another folder":
                    valid_input = False
                else:
                    valid_input = True
                    return file_path
            else:
                print(
                    f"No {file_extension} files found in {input_main_dir}. Please try another location."
                )

    # Process provided path if given
    if provided_path:
        # Try different path variants
        for path_variant in [
            provided_path,
            os.path.join(os.getcwd(), provided_path),
            os.path.abspath(provided_path),
        ]:
            if os.path.exists(path_variant):
                provided_path = path_variant
                break

        # Path doesn't exist
        if not os.path.exists(provided_path):
            raise ValueError(f"The provided path {provided_path} does not exist.")

        # If it's a file with the correct extension
        if os.path.isfile(provided_path) and provided_path.endswith(file_extension):
            return provided_path

        # If it's a directory, find matching files
        elif os.path.isdir(provided_path):
            matching_files = glob.glob(
                os.path.join(provided_path, f"*{file_extension}"), recursive=False
            )
            if matching_files:
                return select_option(
                    matching_files,
                    f"\nSelect a {file_extension} file to run NanoGO Pipeline on:",
                )
            else:
                return loop_check(provided_path)

        # Invalid path type
        else:
            raise ValueError(
                f"The provided path {provided_path} is not a {file_extension} file or directory containing {file_extension} files."
            )

    # No path provided and multiple input folders
    elif all_input_selected:
        user_confirm = select_option(
            ["Yes", "No"], f"Are {file_extension} files located in each input folder?"
        )

        if user_confirm == "Yes":
            list_of_files = []

            for folder in input_folders:
                matching_files = glob.glob(
                    os.path.join(folder, f"*{file_extension}"), recursive=False
                )

                if matching_files and len(matching_files) == 1:
                    list_of_files.append(matching_files[0])
                elif matching_files and len(matching_files) > 1:
                    file_path = select_option(
                        matching_files,
                        f"Multiple {file_extension} files found in {folder}. \nSelect a {file_extension} file to run NanoGO Pipeline on:",
                    )
                    list_of_files.append(file_path)
                else:
                    print(
                        f"\n\u001b[4mNo {file_extension} file found in the path {folder}.\u001b[0m"
                    )
                    file_path = loop_check(folder)
                    list_of_files.append(file_path)

            if not len(list_of_files) == len(input_folders):
                raise ValueError(
                    f"No {file_extension} file found in one or more of the specified folders."
                )

            return list_of_files

        elif user_confirm == "No":
            matching_files = glob.glob(f"*{file_extension}", recursive=False)

            if matching_files:
                file_path = select_option(
                    matching_files + ["Choose another folder."],
                    f"Select a {file_extension} file to run NanoGO Pipeline on:",
                )

                if file_path == "Choose another folder.":
                    return loop_check()

                return file_path
            else:
                print(f"\nNo {file_extension} files found in the current directory.")
                return loop_check()

    # No path provided and single input folder
    else:
        # Convert to string if it's a single-item list
        if isinstance(input_folders, list) and len(input_folders) == 1:
            input_folders = input_folders[0]

        matching_files = glob.glob(
            os.path.join(input_folders, f"*{file_extension}"), recursive=False
        )

        if matching_files:
            file_path = select_option(
                matching_files,
                f"Select {file_extension} file to run NanoGO Pipeline on:",
            )
            return file_path
        else:
            print(
                f"\n\u001b[4mNo {file_extension} files found in the path {input_folders}.\u001b[0m"
            )
            return loop_check()


def interactivate_nanogo_primer_file(
    input_folders: Union[str, List[str]], provided_path: Optional[str] = None
) -> Union[str, List[str]]:
    """
    Interactively select primer files for NanoGO.

    Args:
        input_folders: Input folder(s) to search in
        provided_path: Path provided as an argument, if any

    Returns:
        Selected primer file path(s)
    """
    return interactivate_file_selection(
        input_folders,
        ".txt",
        "Select primer file to run NanoGO Pipeline on:",
        provided_path,
    )


def interactivate_nanogo_reference_file(
    input_folders: Union[str, List[str]], provided_path: Optional[str] = None
) -> Union[str, List[str]]:
    """
    Interactively select reference files for NanoGO.

    Args:
        input_folders: Input folder(s) to search in
        provided_path: Path provided as an argument, if any

    Returns:
        Selected reference file path(s)
    """
    return interactivate_file_selection(
        input_folders,
        ".fasta",
        "Select a reference file to run NanoGO Pipeline on:",
        provided_path,
    )


def get_nanogo_path() -> Optional[str]:
    """Find the installation path of NanoGO."""
    try:
        nanogo_path = subprocess.check_output(["which", "nanogo"]).decode().strip()
        return os.path.dirname(nanogo_path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("nanogo not found in the PATH.")
        return None


def interactivate_kraken_db(provided_path: Optional[str] = None) -> str:
    """Interactively select a Kraken2 database."""

    def loop_check():
        valid_input = False
        while not valid_input:
            input_main_dir = path_check(
                "\nEnter path to folder containing Kraken2 database: "
            )
            kraken2_database = glob.glob(
                os.path.join(input_main_dir, "*.k2d"), recursive=False
            )

            if kraken2_database:
                database_path = select_option(
                    [os.path.dirname(kraken2_database[0])] + ["Choose another folder"],
                    "Select Kraken2 database to run NanoGO Pipeline on:",
                )

                if database_path == "Choose another folder":
                    valid_input = False
                else:
                    valid_input = True
                    return database_path
            else:
                print(
                    f"No Kraken2 database files found in {input_main_dir}. Please try another location."
                )

    # Process provided path if given
    if provided_path:
        # Path exists and is a directory with k2d files
        if os.path.isdir(provided_path):
            database_files = glob.glob(
                os.path.join(provided_path, "*.k2d"), recursive=True
            )
            if database_files:
                return os.path.dirname(database_files[0])
            else:
                return loop_check()
        else:
            raise ValueError(
                f"The provided path {provided_path} is not a directory containing Kraken2 database."
            )

    # No path provided, try default locations
    else:
        # Try default installation locations
        local_database = os.path.join(
            os.path.dirname(os.path.dirname((os.path.abspath(__file__)))), "database"
        )
        nanogo_path = get_nanogo_path()

        if nanogo_path:
            database_rel_nanogo = os.path.join(os.path.dirname(nanogo_path), "database")
            if os.path.exists(database_rel_nanogo):
                return database_rel_nanogo

        if os.path.exists(local_database):
            return local_database

        # Prompt user for database location
        return loop_check()


def interactivate_output_path(
    input_path: Union[str, List[str]],
    output_name: Optional[str] = None,
    overwrite: bool = False,
) -> Union[str, List[str]]:
    """
    Create output directories based on input paths.

    Args:
        input_path: Input path(s) to create output directories for
        output_name: Name of the output directory
        overwrite: Whether to overwrite existing directories

    Returns:
        Path(s) to the created output directories
    """

    base_folder_name = output_name if output_name else get_valid_folder_name()

    # Process a list of input paths
    if isinstance(input_path, list):
        output_folder_names = []

        for path in input_path:
            # If path is a file, use its parent directory
            folder = os.path.dirname(path) if os.path.isfile(path) else path
            folder_name_with_path = os.path.join(folder, base_folder_name)
            unique_output_folder = ensure_unique_folder(
                folder_name_with_path, overwrite
            )
            output_folder_names.append(unique_output_folder)

        return output_folder_names

    # Process a single input path
    else:
        # If path is a file, use its parent directory
        folder = (
            os.path.dirname(input_path) if os.path.isfile(input_path) else input_path
        )
        folder_name_with_path = os.path.join(folder, base_folder_name)
        unique_output_folder = ensure_unique_folder(folder_name_with_path, overwrite)

        return unique_output_folder


# if __name__ == "__main__":
#     print(interactivate_output_path(interactivate_nanogo_input()))
