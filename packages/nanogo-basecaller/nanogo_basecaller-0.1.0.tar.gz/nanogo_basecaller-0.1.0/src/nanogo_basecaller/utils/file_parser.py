"""
File parsing utilities for the NanoGO bioinformatics pipeline.

This module provides functions for reading and parsing different file types
used in sequencing data analysis.
"""

import os
import gzip
from typing import (
    List,
    Dict,
    Any,
    Iterator,
    Union,
    Optional,
    TextIO,
    BinaryIO,
    cast,
    Iterable,
)
from typing import TypeVar, IO

# Define IO type that can handle both text and binary modes
AnyIO = Union[TextIO, BinaryIO]


def open_file(file_path: str, mode: str = "rt") -> AnyIO:
    """
    Open a file with the appropriate function based on file extension.

    Args:
        file_path: Path to the file to open
        mode: File opening mode ('rt', 'rb', 'wt', etc.)

    Returns:
        File object

    Raises:
        FileNotFoundError: If the file does not exist and is being opened for reading
        ValueError: If the mode is not valid
    """
    if "r" in mode and not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.endswith(".gz"):
        return cast(AnyIO, gzip.open(file_path, mode))
    else:
        return cast(AnyIO, open(file_path, mode))


def read_fastq(file_path: str) -> Iterator[Dict[str, str]]:
    """
    Read a FASTQ file and yield record dictionaries.

    Args:
        file_path: Path to the FASTQ file (can be gzipped)

    Yields:
        Dictionary containing 'header', 'sequence', 'plus', and 'quality' keys
    """
    with open_file(file_path, "rt") as f:
        f_text = cast(TextIO, f)  # Ensure we're working with TextIO

        while True:
            # Read 4 lines at a time
            header = f_text.readline().strip()
            if not header:
                break

            sequence = f_text.readline().strip()
            plus = f_text.readline().strip()
            quality = f_text.readline().strip()

            yield {
                "header": str(header),
                "sequence": str(sequence),
                "plus": str(plus),
                "quality": str(quality),
            }


def read_fasta(file_path: str) -> Iterator[Dict[str, str]]:
    """
    Read a FASTA file and yield record dictionaries.

    Args:
        file_path: Path to the FASTA file (can be gzipped)

    Yields:
        Dictionary containing 'header' and 'sequence' keys
    """
    current_header: Optional[str] = None
    current_sequence: List[str] = []

    with open_file(file_path, "rt") as f:
        f_text = cast(TextIO, f)  # Ensure we're working with TextIO

        for line in f_text:
            line_str = str(line).strip()
            if not line_str:
                continue

            if line_str.startswith(">"):
                # If we already have a sequence, yield it before starting a new one
                if current_header is not None:
                    yield {
                        "header": current_header,
                        "sequence": "".join(current_sequence),
                    }

                current_header = line_str
                current_sequence = []
            else:
                current_sequence.append(line_str)

        # Don't forget to yield the last sequence
        if current_header is not None:
            yield {"header": current_header, "sequence": "".join(current_sequence)}


def parse_primers_file(file_path: str) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Parse a primers file containing forward and reverse primers.

    Args:
        file_path: Path to the primers file

    Returns:
        Dictionary mapping primer names to dictionaries with 'forward' and 'reverse' keys

    Example primer file format:
        >primer1-F
        ACGTACGT
        >primer1-R
        TGCATGCA
    """
    primers: Dict[str, Dict[str, Optional[str]]] = {}
    current_name: Optional[str] = None
    direction: Optional[str] = None

    with open_file(file_path, "rt") as f:
        f_text = cast(TextIO, f)  # Ensure we're working with TextIO

        for line in f_text:
            line_str = str(line).strip()
            if not line_str:
                continue

            if line_str.startswith(">"):
                # Parse primer name and direction
                full_name = line_str[1:]  # Remove '>'

                # Check for -F or -R suffix
                if full_name.endswith("-F"):
                    base_name = full_name[:-2]
                    direction = "forward"
                elif full_name.endswith("-R"):
                    base_name = full_name[:-2]
                    direction = "reverse"
                else:
                    raise ValueError(f"Primer name must end with -F or -R: {full_name}")

                current_name = base_name

                # Initialize primer entry if not exists
                if current_name not in primers:
                    primers[current_name] = {"forward": None, "reverse": None}

            else:
                # This is the sequence line
                if current_name is None or direction is None:
                    raise ValueError("Sequence found before primer name")

                assert direction in [
                    "forward",
                    "reverse",
                ], "Direction must be 'forward' or 'reverse'"

                primers[current_name][direction] = line_str
                current_name = None
                direction = None

    # Convert to expected return type
    # This is a safe conversion since we've filled in all the values properly
    return cast(Dict[str, Dict[str, str]], primers)
