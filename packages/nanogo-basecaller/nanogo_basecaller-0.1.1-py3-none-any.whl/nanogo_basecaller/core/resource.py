"""
Resource allocation functionality for the NanoGO bioinformatics pipeline.
"""

import math
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None


class ResourceAllocator:
    """Manages resource allocation for parallel processes."""

    def __init__(
        self,
        cores_required=4,
        memory_required=16,
        gpus_required=1,
        cpu_buffer_ratio=0.8,
        memory_buffer_ratio=0.8,
        gpu_buffer_ratio=0.8,
    ):
        """
        Initializes the ResourceAllocator with required resources per process.

        Args:
            cores_required: The number of CPU cores required per process.
            memory_required: The amount of memory required per process in GB.
            gpus_required: The number of GPUs required per process.
            cpu_buffer_ratio: Fraction of total CPU cores to be used (default 0.8).
            memory_buffer_ratio: Fraction of available memory to be used (default 0.8).
            gpu_buffer_ratio: Fraction of available GPUs to be used (default 0.8).
        """
        self.cores_required = cores_required
        # Convert the required memory from GB to bytes.
        self.memory_required = memory_required * 1024**3
        self.gpus_required = gpus_required
        self.cpu_buffer_ratio = cpu_buffer_ratio
        self.memory_buffer_ratio = memory_buffer_ratio
        self.gpu_buffer_ratio = gpu_buffer_ratio

    def get_available_gpus(self):
        """
        Get list of available GPU IDs that meet load and memory requirements.

        Returns:
            List of available GPU IDs or empty list if GPUtil is not available.
        """
        if GPUtil:
            return GPUtil.getAvailable(
                limit=100,
                maxLoad=0.5,
                maxMemory=0.5,
                includeNan=False,
                excludeID=[],
                excludeUUID=[],
            )
        return []

    def resource_allowance_gpu(self):
        """
        Calculates the maximum number of processes that can be executed concurrently
        based on the system's available resources, including GPU availability.

        Uses configurable buffer ratios so that not all resources are used.

        Returns:
            The minimum number of processes allowed by CPU, memory, and GPU availability.
        """
        # Use only a fraction of available memory.
        available_memory = psutil.virtual_memory().available * self.memory_buffer_ratio
        max_processes_by_memory = max(1, int(available_memory / self.memory_required))

        # Use only a fraction of total CPU cores.
        total_cpu = psutil.cpu_count(logical=True)  # Use logical cores.
        available_cpu = int(total_cpu * self.cpu_buffer_ratio)
        max_processes_by_cpu = max(1, int(available_cpu / self.cores_required))

        if GPUtil:
            try:
                available_gpus = self.get_available_gpus()
                # Reserve only a fraction of available GPUs.
                allowed_gpus = int(len(available_gpus) * self.gpu_buffer_ratio)
                max_processes_by_gpu = max(1, allowed_gpus // self.gpus_required)
            except Exception:
                max_processes_by_gpu = 1
        else:
            max_processes_by_gpu = 1

        return min(max_processes_by_memory, max_processes_by_cpu, max_processes_by_gpu)

    def resource_allowance(self):
        """
        Calculates the maximum number of processes that can be executed concurrently
        based on the system's available resources (CPU and memory).

        Uses configurable buffer ratios so that not all resources are allocated.

        Returns:
            The minimum number of processes allowed by CPU and memory.
        """
        available_memory = psutil.virtual_memory().available * self.memory_buffer_ratio
        max_processes_by_memory = max(1, int(available_memory / self.memory_required))

        total_cpu = psutil.cpu_count(logical=True)
        available_cpu = int(total_cpu * self.cpu_buffer_ratio)
        max_processes_by_cpu = max(1, int(available_cpu / self.cores_required))

        return min(max_processes_by_memory, max_processes_by_cpu)


if __name__ == "__main__":
    ra = ResourceAllocator()
    print(ra.resource_allowance())
    print(ra.resource_allowance_gpu())
