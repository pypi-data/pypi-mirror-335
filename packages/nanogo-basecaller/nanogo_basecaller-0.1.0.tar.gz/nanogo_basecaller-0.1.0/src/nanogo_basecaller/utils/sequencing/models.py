"""
Utilities for selecting and managing sequencing models.

This module provides functions for listing and selecting models and kits
for various sequencing tools including Dorado and Medaka.
"""

import os
import sys
import hashlib
import subprocess
from typing import List, Optional, Dict, Any
from ...utils.id_extraction import extract_unique_ids, hash_string
from ...utils.cli_select import select_option
from ...core.environment import EnvironmentManager


def list_dorado_models(
    model_type: str = "all", tool_env: Optional[Dict[str, str]] = None
) -> List[str]:
    """
    List available Dorado models.

    Args:
        model_type: Type of models to list ("dna", "rna", or "all")

    Returns:
        List of available model names
    """
    if tool_env is None:
        raise ValueError("tool_env_mapping is required but was not provided.")

    conda_env = EnvironmentManager.conda_tool("dorado", tool_env)

    models = []

    # Get DNA models if requested
    if model_type in ["dna", "all"]:
        dna_models = extract_unique_ids(
            file_path="",
            string_to_find_1="dna",
            string_to_find_2="dna",
            start_string_char="dna",
            end_string_char=" ",
            start_string_position=0,
            end_string_position=1000,
            command="dorado download --list",
            tool_env=conda_env,
        )
        models.extend(dna_models)

    # Get RNA models if requested
    if model_type in ["rna", "all"]:
        rna_models = extract_unique_ids(
            file_path="",
            string_to_find_1="rna",
            string_to_find_2="rna",
            start_string_char="rna",
            end_string_char=" ",
            start_string_position=0,
            end_string_position=1000,
            command="dorado download --list",
            tool_env=conda_env,
        )
        models.extend(rna_models)

    return models


def select_dorado_model(
    prompt: str = "Select a model to use for basecalling:",
    model_type: str = "all",
    hash_output: bool = False,
    tool_env: Optional[Dict[str, str]] = None,
) -> str:
    """
    Present a list of Dorado models and allow the user to select one.

    Args:
        prompt: Prompt text to display
        model_type: Type of models to list ("dna", "rna", or "all")
        hash_output: Whether to hash the selected model name

    Returns:
        Selected model name or its hash
    """

    models = list_dorado_models(model_type, tool_env)
    # print("Available Dorado Models:", models)
    if not models:
        print("No Dorado models found. Make sure Dorado is installed correctly.")
        return ""

    model_selection = select_option(models, prompt)

    if hash_output and model_selection:
        return hash_string(model_selection, 8)

    return model_selection


def list_dorado_kits(tool_env: Optional[str] = None) -> List[str]:
    """
    List available Dorado barcoding kits.

    Returns:
        List of available kit names
    """
    if tool_env is None:
        raise ValueError("tool_env_mapping is required but was not provided.")

    conda_env = EnvironmentManager.conda_tool("dorado", tool_env)

    kits = extract_unique_ids(
        file_path="",
        string_to_find_1="Choose from: EXP",
        string_to_find_2="Choose from: EXP",
        start_string_char="EXP",
        end_string_char="\n",
        start_string_position=13,
        end_string_position=-1,
        command="dorado demux --help",
        tool_env=conda_env,
    )

    # Ensure we got actual kit names
    if not kits:
        try:
            # Fallback to direct command execution if extract_unique_ids fails
            env_path = os.environ.get("CONDA_PREFIX", "")
            cmd = f"{env_path}/bin/dorado demux --help"

            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = result.stdout or result.stderr

            # Attempt to extract kits from output
            for line in output.splitlines():
                if "Choose from: EXP" in line:
                    parts = line.split("Choose from: ")[1].strip()
                    kits = [k.strip() for k in parts.split(",")]
                    break
        except Exception as e:
            print(f"Error getting Dorado kits: {e}")

    return kits


def select_dorado_kit(
    prompt: str = "Select a barcoding kit to use for demultiplexing reads:",
    hash_output: bool = False,
    tool_env: Optional[Dict[str, str]] = None,
) -> str:
    """
    Present a list of Dorado kits and allow the user to select one.

    Args:
        prompt: Prompt text to display
        hash_output: Whether to hash the selected kit name

    Returns:
        Selected kit name or its hash
    """
    kits = list_dorado_kits(tool_env)

    if not kits:
        print("No Dorado kits found. Make sure Dorado is installed correctly.")
        return ""

    kit_selection = select_option(kits, prompt)

    if hash_output and kit_selection:
        return hash_string(kit_selection, 8)

    return kit_selection


def list_medaka_models(tool_env: Optional[str] = None) -> List[str]:
    """
    List available Medaka models.

    Args:
        tool_env: Path to the Medaka environment

    Returns:
        List of available model names
    """

    if tool_env is None:
        raise ValueError("tool_env_mapping is required but was not provided.")

    conda_env = EnvironmentManager.conda_tool("dorado", tool_env)

    models_list = extract_unique_ids(
        file_path="",
        string_to_find_1="r",
        string_to_find_2=",",
        start_string_char="r",
        end_string_char=", \n",
        start_string_position=0,
        end_string_position=0,
        command="medaka tools list_models",
        tool_env=conda_env,
    )

    # Clean up model names
    clean_models = []
    for model in models_list:
        model = model.replace(",", "")
        if model:  # Only add non-empty models
            clean_models.append(model)

    # If extraction failed, try a fallback method
    if not clean_models:
        try:
            if tool_env:
                env_path = tool_env
            else:
                env_path = os.environ.get("CONDA_PREFIX", "")

            cmd = f"{env_path}/bin/medaka tools list_models"
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output = result.stdout or result.stderr

            for line in output.splitlines():
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    for part in parts:
                        part = part.strip()
                        if part and part.startswith("r"):
                            clean_models.append(part)
        except Exception as e:
            print(f"Error getting Medaka models: {e}")

    return clean_models


def select_medaka_model(
    prompt: str = "Select a kit by entering its number:", tool_env: Optional[str] = None
) -> str:
    """
    Present a list of Medaka models and allow the user to select one.

    Args:
        prompt: Prompt text to display
        tool_env: Path to the Medaka environment

    Returns:
        Selected model name
    """
    models = list_medaka_models(tool_env)

    if not models:
        print("No Medaka models found. Make sure Medaka is installed correctly.")
        return ""

    model_selection = select_option(models, prompt)

    # Print selected model for confirmation
    if model_selection:
        print(f"Selected kit: {model_selection}")

    return model_selection


# # For testing
# if __name__ == "__main__":
#     # 1. List all models
#     all_models = list_dorado_models()
#     print("All models:", all_models)

#     # 2. List only DNA models
#     dna_models = list_dorado_models("dna")
#     print("DNA models:", dna_models)

#     # 3. List only RNA models
#     rna_models = list_dorado_models("rna")
#     print("RNA models:", rna_models)


# print("Available Dorado Models:")
# models = list_dorado_models('All')
# for model in models:
#     print(f"  - {model}")

# print("\nAvailable Dorado Kits:")
# kits = list_dorado_kits()
# for kit in kits:
#     print(f"  - {kit}")

# print("\nAvailable Medaka Models:")
# medaka_models = list_medaka_models()
# for model in medaka_models:
#     print(f"  - {model}")
