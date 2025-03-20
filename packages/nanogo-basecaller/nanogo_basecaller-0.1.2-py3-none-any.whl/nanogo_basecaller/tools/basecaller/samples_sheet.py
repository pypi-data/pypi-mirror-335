import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SampleSheetGenerator")


class SampleSheetGenerator:
    """
    Generates sample sheets for Dorado basecalling.

    This class handles the creation of sample sheets used by Dorado for
    basecalling and demultiplexing Oxford Nanopore sequencing data.
    """

    def __init__(self, flow_cell_id, protocol_run_id, basecalling_model_hash):
        """
        Initialize the SampleSheetGenerator with sequencing metadata.

        Args:
            flow_cell_id: ID of the flow cell used in sequencing
            protocol_run_id: ID of the sequencing run
            basecalling_model_hash: Hash of the basecalling model
        """
        self.flow_cell_id = flow_cell_id
        self.protocol_run_id = protocol_run_id
        self.basecalling_model_hash = basecalling_model_hash
        self.experiment_id = (
            f"{flow_cell_id}_{protocol_run_id}_{basecalling_model_hash}"
        )
        self.kit = None
        self.num_barcodes = 0
        logger.debug(
            f"Initialized SampleSheetGenerator with experiment_id: {self.experiment_id}"
        )

    def prompt_for_kit_name(self, kit_name=None):
        """
        Set the kit name, either provided or via user input.

        Args:
            kit_name: Optional kit name, if not provided will prompt user
        """
        if kit_name:
            self.kit = kit_name
            logger.info(f"Using provided kit name: {self.kit}")
        else:
            try:
                self.kit = input("Enter the kit name (e.g., SQK-NBD114-96): ")
                logger.info(f"Kit name set by user input: {self.kit}")
            except Exception as e:
                logger.error(f"Error getting kit name from user: {e}")
                self.kit = "SQK-NBD114-96"  # Default fallback
                logger.info(f"Using default kit name: {self.kit}")

        self.num_barcodes = self.get_num_barcodes()

    def get_num_barcodes(self):
        """
        Determine the number of barcodes from the kit name or user input.

        Returns:
            Number of barcodes in the kit
        """
        try:
            parts = self.kit.split("-")
            if parts[-1].isdigit():
                barcodes = int(parts[-1])
                logger.debug(f"Extracted {barcodes} barcodes from kit name")
                return barcodes
            else:
                try:
                    barcodes = int(
                        input(
                            f"Kit '{self.kit}' does not specify the number of barcodes. Please enter it: "
                        )
                    )
                    logger.debug(f"User specified {barcodes} barcodes")
                    return barcodes
                except ValueError as e:
                    logger.error(f"Invalid number entered: {e}")
                    print("Please enter a valid number.")
                    return self.get_num_barcodes()  # Retry if the input was invalid
        except Exception as e:
            logger.error(f"Error determining number of barcodes: {e}")
            # Default to 96 if we can't determine otherwise
            logger.info("Using default value of 96 barcodes")
            return 96

    def generate_sample_sheet_df(self):
        """
        Generate a DataFrame containing the sample sheet information.

        Returns:
            pandas DataFrame with the sample sheet data
        """
        try:
            base_alias = f"{self.flow_cell_id}_barcode"
            data = {
                "flow_cell_id": [self.flow_cell_id] * self.num_barcodes,
                "experiment_id": [self.experiment_id] * self.num_barcodes,
                "kit": [self.kit] * self.num_barcodes,
                "alias": [
                    f"{base_alias}{i:02d}_{self.protocol_run_id}_{self.basecalling_model_hash}"
                    for i in range(1, self.num_barcodes + 1)
                ],
                "barcode": [f"barcode{i:02d}" for i in range(1, self.num_barcodes + 1)],
            }
            df = pd.DataFrame(data)
            logger.info(f"Generated sample sheet with {len(df)} entries")
            return df
        except Exception as e:
            logger.error(f"Error generating sample sheet DataFrame: {e}")
            # Create a minimal dataframe with at least one entry to prevent downstream failures
            logger.info("Creating fallback minimal sample sheet")
            return pd.DataFrame(
                {
                    "flow_cell_id": [self.flow_cell_id],
                    "experiment_id": [self.experiment_id],
                    "kit": [self.kit or "unknown"],
                    "alias": [
                        f"{self.flow_cell_id}_barcode01_{self.protocol_run_id}_{self.basecalling_model_hash}"
                    ],
                    "barcode": ["barcode01"],
                }
            )

    def save_sample_sheet_to_csv(self, df, output_path="new_sample_sheet.csv"):
        """
        Save the sample sheet DataFrame to a CSV file.

        Args:
            df: pandas DataFrame to save
            output_path: Path where the CSV will be saved

        Returns:
            Path to the saved CSV file
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Save the DataFrame to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"CSV file has been created at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving sample sheet to CSV: {e}")
            # Try to save to a fallback location
            fallback_path = os.path.join(os.getcwd(), "fallback_sample_sheet.csv")
            try:
                df.to_csv(fallback_path, index=False)
                logger.info(f"Saved sample sheet to fallback location: {fallback_path}")
                return fallback_path
            except Exception as e2:
                logger.error(f"Failed to save sample sheet to fallback location: {e2}")
                return None
