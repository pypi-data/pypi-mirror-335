"""
Dorado basecaller implementation for the NanoGO bioinformatics pipeline.

This module contains the core functionality for basecalling using Dorado with either
standard or duplex basecalling modes. It handles fast5 to pod5 conversion, model
downloading, batch processing, and demultiplexing.
"""

import os
import sys
import glob
import shutil
import hashlib
import time
from itertools import cycle
from pathlib import Path
from alive_progress import alive_bar

from ...tools.versions.version_checker import VersionChecker

# Core imports
from ...core.environment import EnvironmentManager
from ...core.command import CommandBuilder
from ...core.parallel import ParallelProcessor
from ...core.resource import ResourceAllocator

# Utils imports
from ...utils.sequencing.models import select_dorado_model, select_dorado_kit
from ...utils.sequencing.extractors import extract_identifiers
from ...utils.paths import recursive_delete

from ...data_indexer import IndexData

# Basecaller-specific imports
from .samples_sheet import SampleSheetGenerator


class DoradoBasecaller:
    """Implements ONT basecalling using the Dorado tool with GPU acceleration."""

    def __init__(self):
        """Initialize the DoradoBasecaller."""
        self.env_paths = {}

    def version_check(self, required_versions=None):
        """
        Verify that required tool versions are installed.

        Args:
            required_versions: Optional dict of tool version requirements

        Returns:
            Tuple of (tool_versions, tool_env_mapping)

        Raises:
            VersionCheckFailed: If version check fails
        """

        class VersionCheckFailed(Exception):
            pass

        if required_versions is None:
            required_versions = {
                "dorado": "0.6.0",
                "pod5": "0.3.0",
            }

        checker = VersionChecker(required_versions)
        try:
            checker.check_versions()
        except VersionCheckFailed:
            print("Version check failed.")
            sys.exit(1)
        tool_versions = checker.get_final_environment_mapping()
        tool_env_mapping = checker.get_installed_versions()
        return tool_versions, tool_env_mapping

    def prepare_data(
        self,
        slurm_status,
        partition,
        input_folder,
        num_gpus,
        output_folder,
        tool_env_mapping,
    ):
        """
        Prepare input data for basecalling by organizing files and creating sample sheets.

        Args:
            slurm_status: Whether Slurm is being used
            partition: Slurm partition to use
            input_folder: Input folder(s) containing raw data
            num_gpus: Number of GPUs or processing chunks to use
            output_folder: Output folder(s) for results
            tool_env_mapping: Tool environment mapping

        Returns:
            Dictionary of results containing prepared data
        """
        if isinstance(input_folder, str):
            input_folder = [input_folder]
        if isinstance(output_folder, str):
            output_folder = [output_folder]

        # Select models and kits
        try:
            dorado_models = select_dorado_model(tool_env=tool_env_mapping)
        except ValueError:
            print(
                "\033[1;31mError: Unable to fetch Dorado models. Using default model.\033[0m"
            )
            dorado_models = "dna_r10.4.1_e8.2_400bps_sup@v5.0.0"

        try:
            dorado_kits = select_dorado_kit(tool_env=tool_env_mapping)
        except ValueError:
            print(
                "\033[1;31mError: Unable to fetch Dorado kits. Using default kit.\033[0m"
            )
            dorado_kits = "SQK-NBD114-96"

        file_counter = 0
        ont_data_dict = {}
        raw_ont_data = []
        results = {}

        # Find POD5/FAST5 files and organize them
        for idx, folders in enumerate(input_folder):
            pod5_files = glob.glob(os.path.join(folders, "*.pod5"), recursive=True)
            fast5_files = glob.glob(os.path.join(folders, "*.fast5"), recursive=True)

            if pod5_files:
                ont_data_dict[folders] = pod5_files
                raw_ont_data.extend(pod5_files)
            elif fast5_files:
                fast5_conversion = self.convert_fast5_to_pod5(
                    slurm_status,
                    partition,
                    folders,
                    output_folder[idx],
                    tool_env_mapping,
                )
                ont_data_dict[folders] = fast5_conversion
            else:
                print("No pod5 or fast5 files found")

        # Process each input dataset
        for idx, key in enumerate(ont_data_dict):
            # Get flow cell and run IDs
            pod5_file = ont_data_dict[key][0]

            # Extract flow cell ID using dorado_index
            try:
                run_id = IndexData().dorado_index(
                    pod5_file,
                    flow_cell_id=False,
                    run_id=True,
                    dorado_models=False,
                    dorado_kits=False,
                )[0:8]
                flow_cell_id = IndexData().dorado_index(
                    pod5_file,
                    flow_cell_id=True,
                    run_id=False,
                    dorado_models=False,
                    dorado_kits=False,
                )
            except (ImportError, AttributeError):
                # Fall back to direct extraction
                run_id = "unknown"
                flow_cell_id = "unknown"
                # Try to extract IDs if possible
                try:
                    cmd = f"pod5 view -i 'run_id' {pod5_file}"
                    output = CommandBuilder.run_command(cmd)[0]
                    if output:
                        run_id = output.strip()[0:8]

                    cmd = f"pod5 view -i 'flow_cell_id' {pod5_file}"
                    output = CommandBuilder.run_command(cmd)[0]
                    if output:
                        flow_cell_id = output.strip()
                except Exception as e:
                    print(f"Error extracting IDs: {e}")

            # Hash the model and kit names
            dorado_models_hex = hashlib.sha256(
                dorado_models.encode("utf-8")
            ).hexdigest()[:8]
            dorado_kits_hex = hashlib.sha256(dorado_kits.encode("utf-8")).hexdigest()[
                :8
            ]

            # Create temp directory structure
            temp_data_path = os.path.join(output_folder[idx], "temp_data")
            try:
                if os.path.exists(temp_data_path):
                    shutil.rmtree(temp_data_path)
                os.makedirs(temp_data_path, exist_ok=True)
            except OSError as e:
                print(f"Error creating directory: {e}")
                print(f"Current working directory: {os.getcwd()}")
                print(
                    f"Directory permissions: {oct(os.stat(os.path.dirname(temp_data_path)).st_mode)[-3:]}"
                )
                raise

            # Create sample sheet
            samples_sheet_output = os.path.join(
                temp_data_path,
                f"{flow_cell_id}_{run_id}_{dorado_models_hex}_{dorado_kits_hex}_samplesheet.csv",
            )
            generator = SampleSheetGenerator(
                f"{flow_cell_id}", f"{run_id}", f"{dorado_models_hex}"
            )
            generator.prompt_for_kit_name(f"{dorado_kits}")
            df = generator.generate_sample_sheet_df()
            generator.save_sample_sheet_to_csv(df, f"{samples_sheet_output}")

            # Distribute files across GPUs/chunks
            num_files = len(ont_data_dict[key])
            files_per_gpu, remainder = divmod(num_files, num_gpus)
            start = 0
            sublist_directory_list = []

            for gpu_idx in range(num_gpus):
                end = (
                    start + files_per_gpu + (gpu_idx < remainder)
                )  # Calculate end considering the remainder
                sublist_directory = os.path.join(
                    output_folder[idx], "temp_data", f"sublist_{gpu_idx + 1}"
                )
                os.makedirs(sublist_directory, exist_ok=True)
                sublist_directory_list.append(sublist_directory)

                for file_index in range(start, end):
                    file_path = ont_data_dict[key][file_index]
                    file_name = f"{flow_cell_id}_{run_id}_{dorado_models_hex}_{dorado_kits_hex}_{file_counter}.pod5"
                    link_path = os.path.join(sublist_directory, file_name)
                    if os.path.exists(file_path):
                        if os.path.lexists(link_path):
                            os.remove(link_path)
                        os.symlink(file_path, link_path)
                    file_counter += 1

                start = end

            results[key] = [
                temp_data_path,
                output_folder[idx],
                flow_cell_id,
                run_id,
                dorado_models,
                dorado_kits,
                samples_sheet_output,
                sublist_directory_list,
            ]

        return results

    def convert_fast5_to_pod5(
        self, slurm_status, partition, input_folder, output_folder, tool_env_mapping
    ):
        """
        Convert FAST5 files to POD5 format.

        Args:
            slurm_status: Whether Slurm is being used
            partition: Slurm partition to use
            input_folder: Input folder containing FAST5 files
            output_folder: Output folder for POD5 files
            tool_env_mapping: Tool environment mapping

        Returns:
            List of converted POD5 files
        """
        fast5_list = sorted(
            glob.glob(os.path.join(input_folder, "*.fast5"), recursive=True)
        )

        gpu = False
        cores = "2"
        memory = "4"
        prog_promp = "Fast5 files are being converted to pod5 format: "

        if tool_env_mapping is None:
            raise ValueError("tool_env_mapping is required but was not provided.")

        conda_env = EnvironmentManager.conda_tool("dorado", tool_env_mapping)

        commands = []
        fast5_conversion_list = []

        for i, files in enumerate(fast5_list):
            # basename_file = os.path.dirname(files)
            file_name = files.split("/")[-1].split(".")[0]
            output_name = f"{os.path.join(output_folder, file_name)}_{i}.pod5"
            fast5_conversion_list.append(output_name)
            tool_path = f"{conda_env}/bin/pod5 convert fast5 -o {output_name} {files}"
            cmd = CommandBuilder.prepare_command(
                conda_env, slurm_status, partition, tool_path, gpu, cores, memory
            )
            commands.append(cmd)

        ParallelProcessor(
            slurm_status, cores, memory, prog_promp, commands
        ).parellel_analysis()
        return fast5_conversion_list

    def run_basecalling(
        self, slurm_status, partition, tool_env_mapping, results, duplex_mode=False
    ):
        """
        Run the basecalling process with Dorado.

        Args:
            slurm_status: Whether Slurm is being used
            partition: Slurm partition to use
            tool_env_mapping: Tool environment mapping
            results: Results from prepare_data
            duplex_mode: Whether to use duplex basecalling
        """
        gpu = True
        cores = "4"
        memory = "16"

        if tool_env_mapping is None:
            raise ValueError("tool_env_mapping is required but was not provided.")

        conda_env = EnvironmentManager.conda_tool("dorado", tool_env_mapping)

        commands_model_dow = []
        commands_basecaller = []
        commands_demux = []

        def general_model_name(dorado_models):
            """Get a fallback model name."""
            if "sup" in dorado_models:
                return "sup"
            elif "hac" in dorado_models:
                return "hac"
            else:
                return "fast"

        # Get available GPUs
        available_gpus = ResourceAllocator().get_available_gpus()
        gpu_cycle = cycle(available_gpus) if available_gpus else cycle([0])

        # Process each dataset
        for idx, key in enumerate(results):
            temp_data_path = results[key][0]
            input_folder = results[key][1]
            flow_cell_id = results[key][2]
            run_id = results[key][3]
            dorado_models = results[key][4]
            dorado_kits = results[key][5]
            samples_sheet_output = results[key][6]
            sublist_path = results[key][7]

            # Process each data chunk
            for i, folders in enumerate(sublist_path):
                current_gpu = next(gpu_cycle)  # Get the next GPU from the cycle
                gpu_device = f"cuda:{current_gpu}"

                # Prepare file names
                dorado_models_hex = hashlib.sha256(
                    dorado_models.encode("utf-8")
                ).hexdigest()[:8]
                dorado_kits_hex = hashlib.sha256(
                    dorado_kits.encode("utf-8")
                ).hexdigest()[:8]
                output_file = os.path.join(
                    folders,
                    f"{flow_cell_id}_{run_id}_{dorado_models_hex}_{dorado_kits_hex}_output_{i+1}.bam",
                )

                # Download model
                tool_path_model = f"{conda_env}/bin/dorado download --model {dorado_models} --directory {temp_data_path}"
                cmd_model_dow = CommandBuilder.prepare_command(
                    conda_env,
                    slurm_status,
                    partition,
                    tool_path_model,
                    gpu,
                    cores,
                    memory,
                )
                commands_model_dow.append(cmd_model_dow)

                # Prepare basecalling commands
                if duplex_mode:
                    if slurm_status:
                        tool_path_usr_model = f'{conda_env}/bin/dorado duplex --device "cuda:all" {os.path.join(input_folder, "temp_data", dorado_models)} {folders} > {output_file}'
                        cmd_basecaller_1 = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_usr_model,
                            gpu,
                            cores,
                            memory,
                        )
                        tool_path_alt_model = f'{conda_env}/bin/dorado duplex --device "cuda:all" {general_model_name(dorado_models)} {folders} > {output_file}'
                        cmd_basecaller_2 = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_alt_model,
                            gpu,
                            cores,
                            memory,
                            summary_file=None,
                            alternative_tool_path=True,
                        )
                        commands_basecaller.append(cmd_basecaller_1 + cmd_basecaller_2)
                        progress_message = "Performing duplex basecalling"
                    else:
                        tool_path_usr_model = f'{conda_env}/bin/dorado duplex --device "{gpu_device}" {os.path.join(input_folder, "temp_data",dorado_models)} {folders} > {output_file}'
                        tool_path_usr_model += f' || {conda_env}/bin/dorado duplex --device "{gpu_device}" {general_model_name(dorado_models)} {folders} > {output_file}'
                        cmd_basecaller = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_usr_model,
                            gpu,
                            cores,
                            memory,
                        )
                        commands_basecaller.append(cmd_basecaller)
                        progress_message = "Performing duplex basecalling"
                else:
                    if slurm_status:
                        tool_path_usr_model = f'{conda_env}/bin/dorado basecaller --device "cuda:all" --sample-sheet {samples_sheet_output} --barcode-both-ends {os.path.join(input_folder, "temp_data", dorado_models)} {folders} > {output_file}'
                        cmd_basecaller_1 = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_usr_model,
                            gpu,
                            cores,
                            memory,
                        )
                        tool_path_alt_model = f'{conda_env}/bin/dorado basecaller --device "cuda:all" --sample-sheet {samples_sheet_output} --barcode-both-ends {general_model_name(dorado_models)} {folders} > {output_file}'
                        cmd_basecaller_2 = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_alt_model,
                            gpu,
                            cores,
                            memory,
                            summary_file=None,
                            alternative_tool_path=True,
                        )
                        commands_basecaller.append(cmd_basecaller_1 + cmd_basecaller_2)
                        progress_message = "Performing standard basecalling"
                    else:
                        tool_path_usr_model = f'{conda_env}/bin/dorado basecaller --device "{gpu_device}" --sample-sheet {samples_sheet_output} --barcode-both-ends {os.path.join(input_folder, "temp_data", dorado_models)} {folders} > {output_file}'
                        tool_path_usr_model += f' || {conda_env}/bin/dorado basecaller --device "{gpu_device}" --sample-sheet {samples_sheet_output} --barcode-both-ends {general_model_name(dorado_models)} {folders} > {output_file}'
                        cmd_basecaller = CommandBuilder.prepare_command(
                            conda_env,
                            slurm_status,
                            partition,
                            tool_path_usr_model,
                            gpu,
                            cores,
                            memory,
                        )
                        commands_basecaller.append(cmd_basecaller)
                        progress_message = "Performing standard basecalling"

                # Demux command
                tool_path_demux = f"{conda_env}/bin/dorado demux --output-dir {folders}/demux --emit-fastq --sample-sheet {samples_sheet_output} --kit-name {dorado_kits} {output_file}"
                cmd_demux = CommandBuilder.prepare_command(
                    conda_env,
                    slurm_status,
                    partition,
                    tool_path_demux,
                    gpu,
                    cores,
                    memory,
                )
                commands_demux.append(cmd_demux)

        # Run downloads, basecalling, and demultiplexing
        ParallelProcessor(
            slurm_status,
            cores,
            memory,
            "Downloading basecalling model",
            commands_model_dow,
        ).parellel_analysis()
        ParallelProcessor(
            slurm_status,
            cores,
            memory,
            progress_message,
            commands_basecaller,
            gpu_required=True,
        ).parellel_analysis()
        time.sleep(5)
        ParallelProcessor(
            slurm_status,
            cores,
            memory,
            "Demultiplexing in progress",
            commands_demux,
            gpu_required=True,
        ).parellel_analysis()

    def rename_files(self, results):
        """
        Rename and organize files after basecalling and demultiplexing.

        Args:
            results: Results from prepare_data
        """
        for idx, key in enumerate(results):
            dorado_data_path_initial = results[key][1]
            run_id = results[key][2]

            # Find demultiplexed FASTQ files
            demultiplex_data_path = sorted(
                glob.glob(
                    os.path.join(
                        dorado_data_path_initial, "**", "demux*", "**", "*.fastq"
                    ),
                    recursive=True,
                )
            )

            # Create output directory structure
            final_basecalled_dir = os.path.join(
                dorado_data_path_initial, "final_output"
            )
            dest_folder = glob.glob(
                os.path.join(final_basecalled_dir, "*"), recursive=True
            )

            if os.path.exists(final_basecalled_dir):
                recursive_delete(final_basecalled_dir)
                os.makedirs(final_basecalled_dir)
            else:
                os.makedirs(final_basecalled_dir)

            # Determine barcode folders to create
            barcode_folders = []
            for files in demultiplex_data_path:
                protocol_run_id, basecalling_barcode, basecalling_model = (
                    extract_identifiers(files)
                )
                if basecalling_barcode not in barcode_folders:
                    barcode_folders.append(basecalling_barcode)

            # Create barcode folders
            for folder in barcode_folders:
                os.makedirs(os.path.join(final_basecalled_dir, folder))

            # Track file counts per barcode
            base_name_counts = {}

            # Rename files with a progress bar
            try:

                with alive_bar(
                    len(demultiplex_data_path),
                    title=f"\033[1;31mRenaming files for\033[0m \033[1m{key}\033[0m",
                    spinner="classic",
                    theme="classic",
                    stats=False,
                    elapsed=False,
                    monitor=True,
                ) as bar:
                    self._rename_files_with_progress(
                        demultiplex_data_path, base_name_counts, run_id, bar
                    )
            except ImportError:
                self._rename_files_without_progress(
                    demultiplex_data_path, base_name_counts, run_id
                )

            # Get destination folders and updated demultiplexed data paths
            dest_folder = glob.glob(
                os.path.join(final_basecalled_dir, "*"), recursive=True
            )
            demultiplex_data_path = glob.glob(
                os.path.join(dorado_data_path_initial + "/**/demux*" + "/**/*.fastq"),
                recursive=True,
            )

            # Move files to their barcode folders
            try:
                with alive_bar(
                    len(demultiplex_data_path),
                    title=f"\033[1;31mMoving files for\033[0m \033[1m{key}\033[0m",
                    spinner="classic",
                    theme="classic",
                    stats=False,
                    elapsed=False,
                    monitor=True,
                ) as bar:
                    self._move_files_with_progress(
                        demultiplex_data_path, dest_folder, final_basecalled_dir, bar
                    )
            except ImportError:
                self._move_files_without_progress(
                    demultiplex_data_path, dest_folder, final_basecalled_dir
                )

    def _rename_files_with_progress(
        self, demultiplex_data_path, base_name_counts, run_id, bar
    ):
        """Helper method to rename files with progress tracking."""
        for files in demultiplex_data_path:
            protocol_run_id, basecalling_barcode, basecalling_model = (
                extract_identifiers(files)
            )
            dorado_models_hex = hashlib.sha256(
                basecalling_model.encode("utf-8")
            ).hexdigest()[:8]

            dir_name_extr = os.path.dirname(files)
            if basecalling_barcode not in base_name_counts:
                base_name_counts[basecalling_barcode] = 0

            run_8hex_1 = protocol_run_id[:8]
            run_8hex_2 = dorado_models_hex
            barcode_num = basecalling_barcode

            base_name_counts[basecalling_barcode] += 1
            file_count = base_name_counts[basecalling_barcode]

            new_file_name = f"{dir_name_extr}/{run_id}_{barcode_num}_{run_8hex_1}_{run_8hex_2}_{file_count}.fastq"
            shutil.move(files, new_file_name)
            bar()  # Update the progress bar

    def _rename_files_without_progress(
        self, demultiplex_data_path, base_name_counts, run_id
    ):
        """Helper method to rename files without progress tracking."""
        for i, files in enumerate(demultiplex_data_path):
            protocol_run_id, basecalling_barcode, basecalling_model = (
                extract_identifiers(files)
            )
            dorado_models_hex = hashlib.sha256(
                basecalling_model.encode("utf-8")
            ).hexdigest()[:8]

            dir_name_extr = os.path.dirname(files)
            if basecalling_barcode not in base_name_counts:
                base_name_counts[basecalling_barcode] = 0

            run_8hex_1 = protocol_run_id[:8]
            run_8hex_2 = dorado_models_hex
            barcode_num = basecalling_barcode

            base_name_counts[basecalling_barcode] += 1
            file_count = base_name_counts[basecalling_barcode]

            new_file_name = f"{dir_name_extr}/{run_id}_{barcode_num}_{run_8hex_1}_{run_8hex_2}_{file_count}.fastq"
            shutil.move(files, new_file_name)
            if (i + 1) % 10 == 0:  # Print progress every 10 files
                print(f"Renamed {i + 1}/{len(demultiplex_data_path)} files")

    def _move_files_with_progress(
        self, demultiplex_data_path, dest_folder, final_basecalled_dir, bar
    ):
        """Helper method to move files with progress tracking."""
        for path in demultiplex_data_path:
            for folders in dest_folder:
                dest_split = folders.split("/")[-1]
                if dest_split in path:
                    shutil.copy(path, os.path.join(final_basecalled_dir, dest_split))
            bar()  # Update the progress bar

    def _move_files_without_progress(
        self, demultiplex_data_path, dest_folder, final_basecalled_dir
    ):
        """Helper method to move files without progress tracking."""
        for i, path in enumerate(demultiplex_data_path):
            for folders in dest_folder:
                dest_split = folders.split("/")[-1]
                if dest_split in path:
                    shutil.copy(path, os.path.join(final_basecalled_dir, dest_split))
            if (i + 1) % 10 == 0:  # Print progress every 10 files
                print(f"Moved {i + 1}/{len(demultiplex_data_path)} files")
