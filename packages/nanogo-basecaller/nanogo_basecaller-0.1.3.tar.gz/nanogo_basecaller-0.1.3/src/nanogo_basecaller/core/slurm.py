"""
Slurm integration functionality for the NanoGO bioinformatics pipeline.
"""

import subprocess
import re
from typing import Optional, List, Tuple


class SlurmManager:
    """Manages Slurm-related functionality."""

    class SlurmCheck:
        """Internal class to handle Slurm detection and partition selection."""

        def __init__(self):
            self.selected_partition = None
            self.use_slurm = None

        def cat_info_subprocess(self, command: str) -> str:
            """Run a command and return its output."""
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                return result.stdout.strip()
            except Exception as e:
                print(f"Error running command '{command}': {e}")
                return ""

        def select_option(self, options: List[str], prompt: str) -> str:
            """
            Let the user select an option from a list.

            Args:
                options: List of options to choose from.
                prompt: Prompt to display.

            Returns:
                Selected option.
            """
            if not options:
                print("No options available to select from.")
                return ""
            while True:
                print(prompt)
                for idx, item in enumerate(options, start=1):
                    print(f"{idx}. {item}")
                choice = input(f"Choose an option (1-{len(options)}): ")
                if not choice.strip():
                    print("Invalid entry. Please provide an option.")
                    continue
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        selected_option = options[choice_num - 1]
                        return selected_option
                    else:
                        print("Invalid choice. Please select a valid option.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

        def ask_use_slurm(self) -> bool:
            """
            Ask the user if they want to use Slurm.

            Returns:
                Whether the user wants to use Slurm.
            """
            print("\033[1;31mDo you want to use Slurm for job management?\033[0m")
            options = ["Yes", "No"]
            user_choice = self.select_option(options, "Select Yes or No:")
            self.use_slurm = user_choice.lower() == "yes"
            return self.use_slurm

        def detect_partitions(self) -> List[str]:
            """
            Detect available partitions using dynamic Slurm commands.

            Returns:
                A list of available partition names.
            """
            partitions = []
            # First try using 'scontrol show partition'
            try:
                output = subprocess.run(
                    "scontrol show partition",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if output.returncode == 0:
                    # Extract partition names with regex matching 'PartitionName=XYZ'
                    partitions = re.findall(r"PartitionName=([^\s]+)", output.stdout)
                    partitions = list(set(partitions))  # ensure uniqueness
                else:
                    print("scontrol command returned non-zero exit code.")
            except Exception as e:
                print(f"Error detecting partitions with scontrol: {e}")

            # If no partitions detected, try fallback with 'sinfo'
            if not partitions:
                try:
                    output = subprocess.run(
                        "sinfo -h -o '%P'",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if output.returncode == 0:
                        partitions = output.stdout.strip().split()
                        partitions = list(set(partitions))
                    else:
                        print("sinfo command returned non-zero exit code.")
                except Exception as e:
                    print(f"Error detecting partitions with sinfo: {e}")

            return partitions

        def partition_selection(self) -> Optional[str]:
            """
            Detect Slurm and prompt for partition selection.

            Returns:
                Selected partition or None if Slurm is not available or not wanted.
            """
            # Check if Slurm is available by testing srun.
            try:
                result = subprocess.run(
                    "srun --help",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                srun_available = result.returncode == 0
            except Exception as e:
                print(f"Error checking srun: {e}")
                srun_available = False

            green_text = "\033[1;32m"
            red_text = "\033[1;31m"
            reset_text = "\033[0m"

            if srun_available:
                if self.ask_use_slurm():
                    if self.selected_partition is None:
                        print(f"\nSlurm status: {green_text}Enabled{reset_text}")
                        partitions = self.detect_partitions()
                        if partitions:
                            self.selected_partition = self.select_option(
                                partitions,
                                f"{red_text}Select partition to run NanoGO in:{reset_text}",
                            )
                            return self.selected_partition
                        else:
                            print("No partitions detected on this system.")
                            return None
                    else:
                        print(f"\nSlurm status: {green_text}Enabled{reset_text}")
                        return self.selected_partition
                else:
                    print(f"\nSlurm status: {red_text}Disabled{reset_text}")
            else:
                print(f"\nSlurm status: {red_text}Not available{reset_text}")

            self.use_slurm = False
            return None

    @staticmethod
    def slurm_selection() -> Tuple[bool, Optional[str]]:
        """
        Determines if Slurm is available and which partition to use.

        Returns:
            Tuple of (slurm_status, partition)
        """
        print("\n")
        slurm = SlurmManager.SlurmCheck()
        partition = slurm.partition_selection()
        return (True, partition) if partition else (False, None)


if __name__ == "__main__":
    slurm_status, partition = SlurmManager.slurm_selection()
    print(f"Slurm status: {slurm_status}")
    print(f"Selected partition: {partition}")
