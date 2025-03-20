"""
Base tool runner functionality for the NanoGO bioinformatics pipeline.
"""

from typing import List, Dict, Tuple, Optional, Callable


from .environment import EnvironmentManager
from .command import CommandBuilder
from .parallel import ParallelProcessor


class ToolRunner:
    """Base class for running bioinformatics tools in the pipeline."""

    def __init__(
        self,
        tool_name: str,
        slurm_status: bool,
        partition: Optional[str],
        cores: str = "4",
        memory: str = "16",
        gpu: bool = False,
        progress_prompt: str = "Running tool",
    ):
        """
        Initialize a tool runner with common parameters.

        Args:
            tool_name: Name of the tool to run
            slurm_status: Whether to use Slurm
            partition: Slurm partition to use
            cores: Number of cores to allocate
            memory: Amount of memory in GB
            gpu: Whether GPU is required
            progress_prompt: Text to display in progress bar
        """
        self.tool_name = tool_name
        self.slurm_status = slurm_status
        self.partition = partition
        self.cores = cores
        self.memory = memory
        self.gpu = gpu
        self.progress_prompt = progress_prompt

    def prepare_run_params(
        self,
        tool_env_mapping: Dict[str, str],
        input_folders: List[str],
        output_folders: List[str],
    ) -> Tuple[str, List[str], List[str]]:
        """
        Prepare common parameters for running a tool.

        Args:
            tool_env_mapping: Mapping of tools to their conda environments
            input_folders: Input folder(s)
            output_folders: Output folder(s)

        Returns:
            Tuple of (conda_env, input_folders as list, output_folders as list)
        """
        if isinstance(input_folders, str):
            input_folders = [input_folders]
        if isinstance(output_folders, str):
            output_folders = [output_folders]

        conda_env = EnvironmentManager.conda_tool(self.tool_name, tool_env_mapping)
        return conda_env, input_folders, output_folders

    def build_commands(self, conda_env: str, tool_commands: List[Dict]) -> List[str]:
        """
        Build shell commands for a tool based on command specifications.

        Args:
            conda_env: Path to conda environment
            tool_commands: List of command specifications, each containing:
                - tool_path: The command to execute
                - summary_file: (Optional) File to redirect output to
                - alternative_tool_path: (Optional) Whether this is an alternative tool path

        Returns:
            List of prepared commands ready for execution
        """
        commands = []
        for spec in tool_commands:
            tool_path = spec["tool_path"]
            summary_file = spec.get("summary_file")
            alternative_tool_path = spec.get("alternative_tool_path", False)
            cmd = CommandBuilder.prepare_command(
                conda_env,
                self.slurm_status,
                self.partition,
                tool_path,
                self.gpu,
                self.cores,
                self.memory,
                summary_file,
                alternative_tool_path,
            )
            commands.append(cmd)
        return commands

    def run_parallel_commands(self, commands: List[str]) -> None:
        """
        Run commands in parallel with resource monitoring.

        Args:
            commands: List of commands to run
        """
        # Use the integrated ParallelProcessor directly
        processor = ParallelProcessor(
            self.slurm_status,
            self.cores,
            self.memory,
            self.progress_prompt,
            commands,
            self.gpu,
        )
        processor.parellel_analysis()

    def run_tool(
        self,
        tool_env_mapping: Dict[str, str],
        input_folders: List[str],
        output_folders: List[str],
        build_command_func: Callable,
    ) -> None:
        """
        Run a tool with the given parameters.

        Args:
            tool_env_mapping: Mapping of tools to their conda environments
            input_folders: Input folder(s)
            output_folders: Output folder(s)
            build_command_func: Function that takes (conda_env, input_folders, output_folders)
                                and returns a list of command specifications
        """
        conda_env, input_folders, output_folders = self.prepare_run_params(
            tool_env_mapping, input_folders, output_folders
        )

        # Get command specifications
        tool_commands = build_command_func(conda_env, input_folders, output_folders)

        # Build shell commands
        commands = self.build_commands(conda_env, tool_commands)

        # Run commands in parallel
        self.run_parallel_commands(commands)
