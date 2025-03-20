"""
Classes and functions for handling sequencing metadata.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RunMetadata:
    """Metadata about a sequencing run."""

    run_id: str
    flow_cell_id: Optional[str] = None
    sequencing_kit: Optional[str] = None
    basecalling_model: Optional[str] = None
    sequencing_date: Optional[str] = None
    platform: str = "Oxford Nanopore"

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "flow_cell_id": self.flow_cell_id,
            "sequencing_kit": self.sequencing_kit,
            "basecalling_model": self.basecalling_model,
            "sequencing_date": self.sequencing_date,
            "platform": self.platform,
        }


@dataclass
class SequencingMetadata:
    """Complete metadata for a sequencing dataset."""

    run_metadata: RunMetadata
    barcode: Optional[str] = None
    sample_name: Optional[str] = None
    sample_type: Optional[str] = None
    total_reads: Optional[int] = None
    total_bases: Optional[int] = None

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = self.run_metadata.as_dict()
        result.update(
            {
                "barcode": self.barcode,
                "sample_name": self.sample_name,
                "sample_type": self.sample_type,
                "total_reads": self.total_reads,
                "total_bases": self.total_bases,
            }
        )
        return result

    def get_filename_prefix(self, type_prefix: str = "NanoGO") -> str:
        """
        Generate a standard filename prefix based on metadata.

        Args:
            type_prefix: Prefix indicating the file type or processing stage

        Returns:
            Formatted filename prefix
        """
        run_id = self.run_metadata.run_id[:8] if self.run_metadata.run_id else "Unknown"
        barcode = self.barcode or "unclassified"
        model = (
            self.run_metadata.basecalling_model[:8]
            if self.run_metadata.basecalling_model
            else "Unknown"
        )

        return f"{type_prefix}_{barcode}_{run_id}_{model}"
