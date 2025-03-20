"""
Extractors for sequencing metadata from various file formats.

This module provides classes and functions for extracting sequence identifiers
and metadata from Guppy and Dorado outputs.
"""

import os
import re
import hashlib
from typing import List, Dict, Tuple, Optional, Union
from abc import ABC, abstractmethod

# Simplified imports
try:
    from ..id_extraction import extract_unique_ids, hash_string
except ImportError:

    def extract_unique_ids(file_path=None, **kwargs):
        print("Warning: extract_unique_ids not properly imported")
        return []

    def hash_string(s, length=8):
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:length]


class BaseExtractor(ABC):
    """Abstract base class for sequencing data extractors."""

    @abstractmethod
    def extract_identifiers(
        self, file_path: str, hash_output: bool = False
    ) -> Tuple[str, str, str]:
        """
        Extract protocol ID, barcode, and model information from a file.

        Args:
            file_path: Path to the file
            hash_output: Whether to hash the output

        Returns:
            Tuple of (protocol_run_id, barcode, model)
        """
        pass

    @staticmethod
    def hash_string(string: str, length: int = 8) -> str:
        """
        Hash a string using SHA-256 and truncate to specified length.

        Args:
            string: String to hash
            length: Length of the hash output

        Returns:
            Truncated hash string
        """
        return hashlib.sha256(string.encode("utf-8")).hexdigest()[:length]


class GuppyExtractor(BaseExtractor):
    """Extract identifiers from Guppy-processed files."""

    def extract_identifiers(
        self, file_path: str, hash_output: bool = False
    ) -> Tuple[str, str, str]:
        """
        Extract protocol ID, barcode, and model information from a Guppy-processed file.

        Args:
            file_path: Path to the file
            hash_output: Whether to hash the output

        Returns:
            Tuple of (protocol_run_id, barcode, model)
        """
        # Extract run ID
        protocol_run_id = "Unknown"
        basecalling_model = "Unknown"
        basecalling_barcode = "unclassified"

        try:
            # Extract run ID
            run_id_values = extract_unique_ids(
                file_path=file_path,
                string_to_find_1="runid=",
                string_to_find_2="runid=",
                start_string_char="runid=",
                end_string_char=" ",
                start_string_position=6,
                end_string_position=0,
                hash_generator=False,
            )

            if run_id_values:
                protocol_run_id = run_id_values[0]

                # Extract basecalling model (DNA)
                dorado_dna_models = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="version_id=dna",
                    string_to_find_2="version_id=dna",
                    start_string_char="dna",
                    end_string_char=" ",
                    start_string_position=0,
                    end_string_position=0,
                    hash_generator=False,
                )

                # Extract basecalling model (RNA)
                dorado_rna_models = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="version_id=rna",
                    string_to_find_2="version_id=rna",
                    start_string_char="rna",
                    end_string_char=" ",
                    start_string_position=0,
                    end_string_position=0,
                    hash_generator=False,
                )

                # Determine model
                if dorado_dna_models:
                    basecalling_model = dorado_dna_models[0]
                elif dorado_rna_models:
                    basecalling_model = dorado_rna_models[0]

                # Extract barcode information
                basecalling_barcode_values = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="barcode=",
                    string_to_find_2="barcode=",
                    start_string_char="barcode=",
                    end_string_char=" ",
                    start_string_position=8,
                    end_string_position=0,
                    hash_generator=False,
                )

                if basecalling_barcode_values:
                    basecalling_barcode = basecalling_barcode_values[0]
                else:
                    # Try to extract from filename
                    file_parts = os.path.basename(file_path).split(".")[0].split("_")
                    for item in file_parts:
                        if item.startswith("barcode"):
                            basecalling_barcode = item
                            break
        except Exception as e:
            print(f"Error extracting identifiers with GuppyExtractor: {e}")

        # Apply hash if requested
        if hash_output:
            if protocol_run_id != "Unknown":
                protocol_run_id = self.hash_string(protocol_run_id)
            if basecalling_model != "Unknown":
                basecalling_model = self.hash_string(basecalling_model)

        return protocol_run_id, basecalling_barcode, basecalling_model


class DoradoExtractor(BaseExtractor):
    """Extract identifiers from Dorado-processed files."""

    def extract_identifiers(
        self, file_path: str, hash_output: bool = False
    ) -> Tuple[str, str, str]:
        """
        Extract protocol ID, barcode, and model information from a Dorado-processed file.

        Args:
            file_path: Path to the file
            hash_output: Whether to hash the identifiers

        Returns:
            Tuple of (protocol_run_id, barcode, model)
        """
        protocol_run_id = "Unknown"
        basecalling_model = "Unknown"
        basecalling_barcode = "unclassified"

        try:
            # Extract run ID using RG:Z: pattern
            run_id_values = extract_unique_ids(
                file_path=file_path,
                string_to_find_1="RG:Z:",
                string_to_find_2="RG:Z:",
                start_string_char="RG:Z:",
                end_string_char="_",
                start_string_position=5,
                end_string_position=0,
                hash_generator=False,
            )

            if run_id_values:
                protocol_run_id = run_id_values[0]

                # Extract model information
                dorado_dna_models = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="_dna",
                    string_to_find_2="_dna",
                    start_string_char="_dna",
                    end_string_char="\t",
                    start_string_position=1,
                    end_string_position=0,
                    hash_generator=False,
                )

                dorado_rna_models = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="_rna",
                    string_to_find_2="_rna",
                    start_string_char="_rna",
                    end_string_char="\t",
                    start_string_position=1,
                    end_string_position=0,
                    hash_generator=False,
                )

                # Process model information
                if dorado_dna_models:
                    basecalling_model = self._clean_model_name(dorado_dna_models[0])
                elif dorado_rna_models:
                    basecalling_model = self._clean_model_name(dorado_rna_models[0])

                # Extract barcode information
                barcode_values = extract_unique_ids(
                    file_path=file_path,
                    string_to_find_1="RG:Z:",
                    string_to_find_2="_barcode",
                    start_string_char="_barcode",
                    end_string_char="",
                    start_string_position=1,
                    end_string_position=9,
                    hash_generator=False,
                )

                if barcode_values:
                    basecalling_barcode = barcode_values[0]
                else:
                    # Try to extract from filename
                    file_parts = os.path.basename(file_path).split(".")[0].split("_")
                    for item in file_parts:
                        if item.startswith("barcode"):
                            basecalling_barcode = item
                            break
        except Exception as e:
            print(f"Error extracting identifiers with DoradoExtractor: {e}")

        # Apply hash to identifiers if requested
        if hash_output:
            if protocol_run_id != "Unknown":
                protocol_run_id = self.hash_string(protocol_run_id)
            if basecalling_model != "Unknown":
                basecalling_model = self.hash_string(basecalling_model)

        return protocol_run_id, basecalling_barcode, basecalling_model

    @staticmethod
    def _clean_model_name(model_name: str) -> str:
        """Remove kit information from model name."""
        for prefix in ["_SQK", "_EXP", "_VSK"]:
            if prefix in model_name:
                model_name = model_name.split(prefix)[0]
        return model_name


def extract_identifiers(
    file_path: str, hash_output: bool = False
) -> Tuple[str, str, str]:
    """
    Extract sequencing identifiers from a file using the appropriate extractor.

    This function automatically detects whether to use the Guppy or Dorado extractor
    based on the file contents.

    Args:
        file_path: Path to the file
        hash_output: Whether to hash the output identifiers

    Returns:
        Tuple of (protocol_run_id, barcode, model)
    """
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return ("Unknown", "unclassified", "Unknown")

    # First try with the Guppy extractor
    guppy_extractor = GuppyExtractor()
    protocol_run_id, barcode, model = guppy_extractor.extract_identifiers(
        file_path, hash_output=False
    )

    # If Guppy extraction failed, try with the Dorado extractor
    if protocol_run_id == "Unknown":
        dorado_extractor = DoradoExtractor()
        protocol_run_id, barcode, model = dorado_extractor.extract_identifiers(
            file_path, hash_output=False
        )

    # Apply hashing if requested
    if hash_output:
        if protocol_run_id != "Unknown":
            protocol_run_id = hash_string(protocol_run_id, 8)
        if model != "Unknown":
            model = hash_string(model, 8)

    return protocol_run_id, barcode, model


# # For testing
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1:
#         test_file = sys.argv[1]
#         print(f"Extracting identifiers from {test_file}...")
#         run_id, barcode, model = extract_identifiers(test_file)
#         print(f"Run ID: {run_id}")
#         print(f"Barcode: {barcode}")
#         print(f"Model: {model}")
#     else:
#         print("Usage: python extractors.py <file_path>")
