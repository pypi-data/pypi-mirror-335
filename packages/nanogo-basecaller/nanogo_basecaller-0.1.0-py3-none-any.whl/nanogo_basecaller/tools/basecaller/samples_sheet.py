import pandas as pd


class SampleSheetGenerator:
    def __init__(self, flow_cell_id, protocol_run_id, basecalling_model_hash):
        self.flow_cell_id = flow_cell_id
        self.protocol_run_id = protocol_run_id
        self.basecalling_model_hash = basecalling_model_hash
        self.experiment_id = (
            f"{flow_cell_id}_{protocol_run_id}_{basecalling_model_hash}"
        )
        self.kit = None
        self.num_barcodes = 0

    def prompt_for_kit_name(self, kit_name=None):
        if kit_name:
            self.kit = kit_name
        else:
            self.kit = input("Enter the kit name (e.g., SQK-NBD114-96): ")
        self.num_barcodes = self.get_num_barcodes()

    def get_num_barcodes(self):
        parts = self.kit.split("-")
        if parts[-1].isdigit():
            return int(parts[-1])
        else:
            try:
                return int(
                    input(
                        f"Kit '{self.kit}' does not specify the number of barcodes. Please enter it: "
                    )
                )
            except ValueError:
                print("Please enter a valid number.")
                return self.get_num_barcodes()  # Retry if the input was invalid

    def generate_sample_sheet_df(self):
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
        return pd.DataFrame(data)

    def save_sample_sheet_to_csv(self, df, output_path="new_sample_sheet.csv"):
        df.to_csv(output_path, index=False)
        # print(f"CSV file has been created at: {output_path}")
