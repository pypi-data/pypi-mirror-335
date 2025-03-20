"""
Parallel processing functionality for the NanoGO bioinformatics pipeline.
"""

import threading
import time
import psutil
import concurrent.futures

try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    from alive_progress import alive_bar
except ImportError:
    alive_bar = None

from .command import CommandBuilder
from .resource import ResourceAllocator


class FallbackProgressBar:
    """
    A simple fallback progress bar to display progress and resource stats
    when alive_progress is not available.
    """

    def __init__(self, total, title="Processing", update_interval=1):
        self.total = total
        self.current = 0
        self.title = title
        self.update_interval = update_interval
        self.last_print_time = time.time()

    def text(self, new_text):
        now = time.time()
        if now - self.last_print_time >= self.update_interval:
            print(f"{self.title}: {self.current}/{self.total} - {new_text}", flush=True)
            self.last_print_time = now

    def __call__(self):
        self.current += 1
        print(f"{self.title}: {self.current}/{self.total}", flush=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Finished {self.title}: {self.current}/{self.total}", flush=True)


class ParallelProcessor:
    """Manages parallel execution of commands with resource monitoring."""

    def __init__(
        self,
        slurm_status=False,
        cores_required=4,
        memory_required=16,
        prog_prompt="",
        commands=None,
        gpu_required=False,
    ):
        """
        Initialize the parallel processor.

        Args:
            slurm_status: Whether using Slurm for job management.
            cores_required: Number of cores required per process.
            memory_required: Memory required per process in GB.
            prog_prompt: Progress message to display.
            commands: List of commands to execute.
            gpu_required: Whether GPU is required.
        """
        self.slurm_status = slurm_status
        self.cores_required = int(cores_required)
        self.memory_required = int(memory_required)
        self.prog_prompt = (
            f"\033[1;31m{prog_prompt}\033[0m"
            if prog_prompt
            else "\033[1;31mProcessing commands\033[0m"
        )
        self.commands = commands or []
        self.gpu_required = gpu_required
        self.running = True
        self.resource_allocator = ResourceAllocator(
            self.cores_required, self.memory_required
        )

    def update_resources(self, bar):
        """
        Update resource usage information in the progress indicator.

        Args:
            bar: Progress indicator to update.
        """
        while self.running:
            try:
                cpu_usage = psutil.cpu_percent(interval=0.5)
                memory_usage = psutil.virtual_memory().percent
                resource_text = f"CPU: {cpu_usage:.0f}%, MEM: {memory_usage:.0f}%"

                if GPUtil and self.gpu_required:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        gpu_memory_usage = (
                            f"{gpu.memoryUsed:.0f}/{gpu.memoryTotal:.0f} MB"
                        )
                        resource_text += f", GPU Mem: {gpu_memory_usage}"

                # Update the progress indicator's text
                try:
                    bar.text(resource_text)
                except Exception:
                    pass
            except Exception as e:
                print(f"Resource monitoring error: {e}")
            time.sleep(0.5)

    def _run_command_safe(self, cmd):
        """
        Helper method to execute a command with exception handling.

        Args:
            cmd: Command to execute.

        Returns:
            The result of the command execution (if any).
        """
        try:
            return CommandBuilder.run_command(cmd)
        except Exception as e:
            print(f"Error running command '{cmd}': {e}")
            return None

    def parellel_analysis(self):
        """
        Execute commands in parallel with resource monitoring.

        Uses a ProcessPoolExecutor for parallel execution and displays progress.
        Even if alive_progress is not available, resource stats (CPU, MEM, GPU)
        and overall progress are printed to the console.
        """
        if not self.commands:
            print("No commands to execute.")
            return

        # Determine maximum parallelism based on configuration.
        if self.slurm_status:
            max_workers = max(1, min(25, len(self.commands)))
        elif self.gpu_required:
            max_workers = self.resource_allocator.resource_allowance_gpu()
            max_workers = max(1, max_workers)
        else:
            max_workers = self.resource_allocator.resource_allowance()
            max_workers = max(1, max_workers)

        commands_to_run = list(self.commands)
        total_cmds = len(commands_to_run)
        self.commands.clear()

        # Use alive_bar if available, else our fallback.
        if alive_bar is not None:
            progress_context = alive_bar(
                total_cmds,
                title=self.prog_prompt,
                spinner="pulse",
                theme="classic",
                stats=False,
                elapsed=True,
                monitor=True,
            )
        else:
            progress_context = FallbackProgressBar(total_cmds, title=self.prog_prompt)

        with progress_context as bar:
            # Start resource monitoring in a daemon thread.
            resource_thread = threading.Thread(
                target=self.update_resources, args=(bar,), daemon=True
            )
            resource_thread.start()

            # Use ProcessPoolExecutor for robust parallel processing.
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=max_workers
            ) as executor:
                future_to_cmd = {
                    executor.submit(self._run_command_safe, cmd): cmd
                    for cmd in commands_to_run
                }

                for future in concurrent.futures.as_completed(future_to_cmd):
                    cmd = future_to_cmd[future]
                    try:
                        future.result()
                    except Exception as exc:
                        print(f"Command '{cmd}' generated an exception: {exc}")
                    finally:
                        bar()  # Update progress after each completed command

            self.running = False
            resource_thread.join(timeout=1)
