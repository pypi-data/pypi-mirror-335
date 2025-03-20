"""
File finding utilities for the NanoGO bioinformatics pipeline.
"""

import os
import sys
import glob
import re
from pathlib import Path
from typing import List, Tuple, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .path_translator import is_ignored_directory
except ImportError:
    # Fallback implementation if the import fails
    def is_ignored_directory(directory, ignore_patterns):
        for pattern in ignore_patterns:
            if re.search(pattern, str(directory)):
                return True
        return False


def find_files_by_pattern(
    base_path: str,
    file_patterns: List[str],
    ignore_patterns: List[str] = [],
    recursive: bool = True,
) -> List[str]:
    """Find files matching patterns in a directory, excluding ignored directories."""

    matching_files = []

    for root, dirs, files in os.walk(base_path, topdown=True):
        # Skip ignored directories
        if recursive:
            dirs[:] = [
                d
                for d in dirs
                if not is_ignored_directory(Path(root) / d, ignore_patterns)
            ]

        for file in files:
            for pattern in file_patterns:
                if glob.fnmatch.fnmatch(file, pattern):
                    file_path = os.path.join(root, file)
                    matching_files.append(file_path)

        if not recursive:
            break

    return matching_files


# if __name__ == '__main__':
#     find_files_by_pattern(
#         base_path='/home/gosahan/nanogo_upgrade_2025/nanogo/example_input/analysis_input',
#         file_patterns=['*.fastq'],
#         ignore_patterns=[''],
#         recursive=True
#     )
#     print("Files found:" + str(find_files_by_pattern) + "\n")
