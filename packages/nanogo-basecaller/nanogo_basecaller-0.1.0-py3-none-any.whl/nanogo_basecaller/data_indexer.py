"""
Data indexing functionality for the NanoGO bioinformatics pipeline.

This module provides backward compatibility with the original data_indexer.py
while leveraging the new modular utility components.
"""

import os
import hashlib
import subprocess
import gzip
from typing import List, Tuple, Optional, Dict, Any, Union


from .utils.id_extraction import extract_unique_ids
from .utils.cli_select import select_option
from .utils.sequencing.extractors import extract_identifiers
from .utils.sequencing.models import (
    select_dorado_model,
    select_dorado_kit,
    select_medaka_model,
)


class IndexData:
    """
    Legacy class providing backward compatibility with the original IndexData class.

    This class uses the new modular components under the hood when available,
    but falls back to the original implementation when needed.
    """

    def __init__(self):
        self.env_paths = {}

    def unique_id_extraction(
        self,
        file_path,
        string_to_find_1=str(),
        string_to_find_2=str(),
        start_string_char=str(),
        end_string_char=str(),
        start_string_position=int(),
        end_string_position=int(),
        length_of_hash=int(),
        command=str(),
        tool_env=None,
        hash_generator=False,
    ):
        """
        Extract unique identifiers from a file or command output based on string patterns.

        Args:
            file_path: Path to the file to extract IDs from. If empty, assumes command execution.
            string_to_find_1: First string pattern to search for
            string_to_find_2: Second string pattern to search for
            start_string_char: String that marks the start of the ID
            end_string_char: String that marks the end of the ID
            start_string_position: Position offset from the start string
            end_string_position: Position offset from the end string
            length_of_hash: Length of hash to generate if hash_generator is True
            command: Command to execute if file_path is empty
            tool_env: Environment path for tool execution
            hash_generator: Whether to generate a hash of the extracted ID

        Returns:
            List of unique IDs extracted
        """
        # Use new component if available
        if extract_unique_ids is not None:
            return extract_unique_ids(
                file_path=file_path,
                string_to_find_1=string_to_find_1,
                string_to_find_2=string_to_find_2,
                start_string_char=start_string_char,
                end_string_char=end_string_char,
                start_string_position=start_string_position,
                end_string_position=end_string_position,
                length_of_hash=length_of_hash,
                command=command,
                tool_env=tool_env,
                hash_generator=hash_generator,
            )

        # Original implementation as fallback
        unique_id = []
        if file_path.endswith(".gz") or file_path.endswith(".fastq"):
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

        elif not file_path:  # Assuming this means run a command
            if tool_env:
                env_path = tool_env
            else:
                env_path = os.environ.get("CONDA_PREFIX", "")
            command_exe = subprocess.run(
                [f"{env_path}/bin/{command}"],
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
                if (
                    not string_to_find_1 and not string_to_find_2
                ):  # No specific string to find
                    item = (
                        hashlib.sha256(value.encode("utf-8")).hexdigest()[
                            :length_of_hash
                        ]
                        if hash_generator
                        else value
                    )
                    if item not in unique_id:
                        unique_id.append(item)
                elif string_to_find_1 in value and string_to_find_2 in value:
                    start_index = value.find(string_to_find_1) + start_string_position
                    end_index = (
                        value.find(end_string_char, start_index) + end_string_position
                    )
                    extracted_id = value[start_index:end_index]
                    if hash_generator:
                        if extracted_id not in unique_id:
                            for value in extracted_id.split(" "):
                                value = hashlib.sha256(
                                    value.encode("utf-8")
                                ).hexdigest()[:length_of_hash]
                                if value not in unique_id:
                                    unique_id.append(value)
                    elif extracted_id not in unique_id:
                        for value in extracted_id.split(" "):
                            if value not in unique_id:
                                unique_id.append(value)
        return unique_id

    def select_option(self, options, prompt, include_all=False):
        """
        Present a list of options to the user and get their selection.

        Args:
            options: List of options to present
            prompt: Prompt text to display
            include_all: Whether to include an "All" option

        Returns:
            Selected option or "All" if that option was selected
        """
        # Use new component if available
        if select_option is not None:
            return select_option(options, prompt, include_all=include_all)

        # Original implementation as fallback
        while True:
            print(prompt)
            for idx, item in enumerate(options, start=1):
                print(f"\033[1;31m{idx}.\033[0m {item}")
            if include_all:
                print(f"{len(options) + 1}. All")
            choice = input(
                f"\033[1;31mChoose an option (1-{len(options) + (1 if include_all else 0)}): \033[0m"
            )
            if not choice.strip():
                print("Invalid entry. Please provide an option.")
                continue
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                elif include_all and choice_num == len(options) + 1:
                    return "All"
                else:
                    print(
                        "\033[1;31mInvalid choice. Please select a valid option.\033[0m"
                    )
            except ValueError:
                print("\033[1;31mInvalid input. Please enter a valid number.\033[0m")

    def guppy_dorodo_index(self, file_path, hash_generator=False):
        """
        Extract identifiers from a Guppy/Dorado processed file.

        Args:
            file_path: Path to the file
            hash_generator: Whether to hash the identifiers

        Returns:
            Tuple of (protocol_run_id, barcode, model)
        """
        # Use new component if available
        if extract_identifiers is not None:
            return extract_identifiers(file_path, hash_generator)

        # Original implementation as fallback
        guppy_extraction = self.unique_id_extraction(
            file_path,
            string_to_find_1="runid=",
            string_to_find_2="runid=",
            start_string_char="runid=",
            end_string_char=" ",
            start_string_position=6,
            end_string_position=0,
            length_of_hash=8,
            hash_generator=False,
        )
        if guppy_extraction:
            protocol_run_id = self.unique_id_extraction(
                file_path,
                string_to_find_1="runid=",
                string_to_find_2="runid=",
                start_string_char="runid=",
                end_string_char=" ",
                start_string_position=6,
                end_string_position=0,
                length_of_hash=8,
                hash_generator=False,
            )[0]
            dorado_dna_models = self.unique_id_extraction(
                file_path,
                string_to_find_1="version_id=dna",
                string_to_find_2="version_id=dna",
                start_string_char="dna",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                hash_generator=False,
            )
            dorado_rna_models = self.unique_id_extraction(
                file_path,
                string_to_find_1="version_id=rna",
                string_to_find_2="version_id=rna",
                start_string_char="rna",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                hash_generator=False,
            )
            if dorado_dna_models:
                basecalling_model = dorado_dna_models[0]
                if hash_generator:
                    basecalling_model = hashlib.sha256(
                        basecalling_model.encode("utf-8")
                    ).hexdigest()[:8]
            elif dorado_rna_models:
                basecalling_model = dorado_rna_models[0]
                if hash_generator:
                    basecalling_model = hashlib.sha256(
                        basecalling_model.encode("utf-8")
                    ).hexdigest()[:8]
            basecalling_barcode = self.unique_id_extraction(
                file_path,
                string_to_find_1="barcode=",
                string_to_find_2="barcode=",
                start_string_char="barcode=",
                end_string_char=" ",
                start_string_position=8,
                end_string_position=0,
                length_of_hash=8,
                hash_generator=False,
            )
            if basecalling_barcode:
                basecalling_barcode = basecalling_barcode[0]
            else:
                file_path = file_path.split("/")[-1].split(".")[0].split("_")
                for item in file_path:
                    if item.startswith("barcode"):
                        basecalling_barcode = item
                if (
                    "basecalling_barcode" not in locals()
                    or len(basecalling_barcode) == 0
                ):
                    basecalling_barcode = "unclassified"
            return protocol_run_id, basecalling_barcode, basecalling_model
        else:
            # If Guppy index extraction failed, attempt to extract the Dorado index
            dorado_extraction = self.unique_id_extraction(
                file_path,
                string_to_find_1="RG:Z:",
                string_to_find_2="RG:Z:",
                start_string_char="RG:Z:",
                end_string_char="_",
                start_string_position=5,
                end_string_position=0,
                length_of_hash=8,
                hash_generator=False,
            )
            if dorado_extraction:
                protocol_run_id = self.unique_id_extraction(
                    file_path,
                    string_to_find_1="RG:Z:",
                    string_to_find_2="RG:Z:",
                    start_string_char="RG:Z:",
                    end_string_char="_",
                    start_string_position=5,
                    end_string_position=0,
                    length_of_hash=8,
                    hash_generator=False,
                )[0]
                dorado_dna_models = self.unique_id_extraction(
                    file_path,
                    string_to_find_1="_dna",
                    string_to_find_2="_dna",
                    start_string_char="_dna",
                    end_string_char="\t",
                    start_string_position=1,
                    end_string_position=0,
                    length_of_hash=8,
                    hash_generator=False,
                )
                dorado_rna_models = self.unique_id_extraction(
                    file_path,
                    string_to_find_1="_rna",
                    string_to_find_2="_rna",
                    start_string_char="_rna",
                    end_string_char="\t",
                    start_string_position=1,
                    end_string_position=0,
                    length_of_hash=8,
                    hash_generator=False,
                )
                if dorado_dna_models:
                    basecalling_model = dorado_dna_models[0]
                    basecalling_model = basecalling_model.split("_SQK")[0]
                    basecalling_model = basecalling_model.split("_EXP")[0]
                    basecalling_model = basecalling_model.split("_VSK")[0]
                    if hash_generator:
                        basecalling_model = hashlib.sha256(
                            basecalling_model.encode("utf-8")
                        ).hexdigest()[:8]
                elif dorado_rna_models:
                    basecalling_model = dorado_rna_models[0]
                    basecalling_model = basecalling_model.split("_SQK")[0]
                    basecalling_model = basecalling_model.split("_EXP")[0]
                    basecalling_model = basecalling_model.split("_VSK")[0]
                    if hash_generator:
                        basecalling_model = hashlib.sha256(
                            basecalling_model.encode("utf-8")
                        ).hexdigest()[:8]
                basecalling_barcode = self.unique_id_extraction(
                    file_path,
                    string_to_find_1="RG:Z:",
                    string_to_find_2="_barcode",
                    start_string_char="_barcode",
                    end_string_char="",
                    start_string_position=1,
                    end_string_position=9,
                    length_of_hash=8,
                    hash_generator=False,
                )
                if basecalling_barcode:
                    basecalling_barcode = basecalling_barcode[0]
                else:
                    file_path = file_path.split("/")[-1].split(".")[0].split("_")
                    for item in file_path:
                        if item.startswith("barcode"):
                            basecalling_barcode = item
                if (
                    "basecalling_barcode" not in locals()
                    or len(basecalling_barcode) == 0
                ):

                    basecalling_barcode = "unclassified"
                return protocol_run_id, basecalling_barcode, basecalling_model

            else:
                print(
                    f"No indices could be extracted from the provided file {file_path}."
                )
                return "Unknown", "Unknown", "Unknown"

    def dorado_index(
        self,
        file_path,
        flow_cell_id=False,
        run_id=False,
        dorado_models=False,
        dorado_kits=False,
        hash_generator=False,
    ):
        """
        Extract Dorado-specific identifiers from files or command output.

        Args:
            file_path: Path to the file
            flow_cell_id: Whether to extract flow cell ID
            run_id: Whether to extract run ID
            dorado_models: Whether to list and select Dorado models
            dorado_kits: Whether to list and select Dorado kits
            hash_generator: Whether to hash the results

        Returns:
            Extracted identifier, selected model, or selected kit
        """
        # Use new components if available
        if flow_cell_id and extract_unique_ids is not None:
            flow_cell_values = extract_unique_ids(
                file_path="",
                string_to_find_1="",
                string_to_find_2="",
                start_string_char="",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                command=f'pod5 view -i "flow_cell_id" {file_path}',
                hash_generator=False,
            )
            if flow_cell_values and len(flow_cell_values) > 1:
                return flow_cell_values[1]

        elif run_id and extract_unique_ids is not None:
            run_id_values = extract_unique_ids(
                file_path="",
                string_to_find_1="",
                string_to_find_2="",
                start_string_char="",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                command=f'pod5 view -i "run_id" {file_path}',
                hash_generator=False,
            )
            if run_id_values and len(run_id_values) > 1:
                return run_id_values[1]

        elif dorado_models and select_dorado_model is not None:
            return select_dorado_model(hash_output=hash_generator)

        elif dorado_kits and select_dorado_kit is not None:
            return select_dorado_kit(hash_output=hash_generator)

        # Original implementation as fallback
        if flow_cell_id:
            flow_cell_id_values = self.unique_id_extraction(
                file_path="",
                string_to_find_1="",
                string_to_find_2="",
                start_string_char="",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                command=f'pod5 view -i "flow_cell_id" {file_path}',
                hash_generator=False,
            )
            if flow_cell_id_values and len(flow_cell_id_values) > 1:
                return flow_cell_id_values[1]

        elif run_id:
            run_id_values = self.unique_id_extraction(
                file_path="",
                string_to_find_1="",
                string_to_find_2="",
                start_string_char="",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=0,
                length_of_hash=8,
                command=f'pod5 view -i "run_id" {file_path}',
                hash_generator=False,
            )
            if run_id_values and len(run_id_values) > 1:
                return run_id_values[1]

        elif not flow_cell_id and not run_id and dorado_models:
            dorado_dna_models = self.unique_id_extraction(
                file_path="",
                string_to_find_1="dna",
                string_to_find_2="dna",
                start_string_char="dna",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=1000,
                length_of_hash=8,
                command="dorado download --list",
                hash_generator=False,
            )
            dorado_rna_models = self.unique_id_extraction(
                file_path="",
                string_to_find_1="rna",
                string_to_find_2="rna",
                start_string_char="rna",
                end_string_char=" ",
                start_string_position=0,
                end_string_position=1000,
                length_of_hash=8,
                command="dorado download --list",
                hash_generator=False,
            )
            dorado_models_list = dorado_dna_models + dorado_rna_models
            model_selection = self.select_option(
                dorado_models_list, "Select a model to use for basecalling: "
            )
            if hash_generator:
                model_selection = hashlib.sha256(
                    model_selection.encode("utf-8")
                ).hexdigest()[:8]
            return model_selection

        elif not flow_cell_id and not run_id and not dorado_models and dorado_kits:
            dorado_kits_list = self.unique_id_extraction(
                file_path="",
                string_to_find_1="Choose from: EXP",
                string_to_find_2="Choose from: EXP",
                start_string_char="EXP",
                end_string_char="\n",
                start_string_position=13,
                end_string_position=-1,
                length_of_hash=8,
                command="dorado demux --help",
                hash_generator=False,
            )
            kit_selection = self.select_option(
                dorado_kits_list,
                "Select a barcoding kit to use for demultiplexing reads: ",
            )
            if hash_generator:
                kit_selection = hashlib.sha256(
                    kit_selection.encode("utf-8")
                ).hexdigest()[:8]
            return kit_selection

        return None

    def medaka_index(self, tool_env=None):
        """
        List and select Medaka models.

        Args:
            tool_env: Path to the Medaka environment

        Returns:
            Selected model name
        """
        # Use new component if available
        if select_medaka_model is not None:
            return select_medaka_model(tool_env=tool_env)

        # Original implementation as fallback
        flow_cell_id = self.unique_id_extraction(
            file_path="",
            string_to_find_1="r",
            string_to_find_2=",",
            start_string_char="r",
            end_string_char=", \n",
            start_string_position=0,
            end_string_position=0,
            length_of_hash=8,
            command="medaka tools list_models",
            tool_env=tool_env,
            hash_generator=False,
        )
        remove_coma = [i.replace(",", "") for i in flow_cell_id]
        model_selection = self.select_option(
            remove_coma, "Select a kit by entering its number: "
        )
        print(f"Selected kit: {model_selection}")
        return model_selection


# if __name__ == "__main__":
#     indexer = IndexData()
#     # indexer.medaka_index('/home/gosahan/miniconda3/envs/nanogo-0.3.8')
#     # IndexData().dorado_index('', flow_cell_id=False, run_id=False, dorado_models=True, dorado_kits=False, hash_generator=False)
#     # IndexData().dorado_index('', flow_cell_id=False, run_id=False, dorado_models=False, dorado_kits=True, hash_generator=False)
#     run_id = IndexData().dorado_index('/home/gosahan/nanogo_upgrade_2025/nanogo/example_input/basecaller_fast5_input/dorado_output/FAV29196_pass_barcode13_3541c09d_e6e45773_0_0.pod5', flow_cell_id=False, run_id=True, dorado_models=False, dorado_kits=False)[0:8]
#     flow_cell_id = IndexData().dorado_index('/home/gosahan/nanogo_upgrade_2025/nanogo/example_input/basecaller_fast5_input/dorado_output/FAV29196_pass_barcode13_3541c09d_e6e45773_0_0.pod5', flow_cell_id=True, run_id=False, dorado_models=False, dorado_kits=False)
#     print(run_id, flow_cell_id)
