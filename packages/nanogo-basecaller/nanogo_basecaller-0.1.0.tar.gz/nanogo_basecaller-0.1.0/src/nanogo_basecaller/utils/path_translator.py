import os


class PathTranslator:
    """
    A class to translate Windows file paths to Linux file paths using in-house drive mappings.
    """

    def __init__(self):
        # Create in-house drive mappings for both "Drives" and "Mnt"
        self.drive_mappings = {
            "Drives": {
                chr(letter): f"/Drives/{chr(letter).lower()}"
                for letter in range(ord("A"), ord("Z") + 1)
            },
            "Mnt": {
                chr(letter): f"/mnt/{chr(letter).lower()}"
                for letter in range(ord("A"), ord("Z") + 1)
            },
        }

    def translate_path(self, file_path: str) -> str:
        """
        Convert a Windows file path to a Linux file path using the in-house drive mappings.

        The method:
          - Normalizes the path by replacing backslashes with forward slashes.
          - Checks for WSL paths and converts them to standard Linux paths.
          - If a Windows drive letter is detected, it constructs two potential paths based on both
            'Drives' and 'Mnt' mappings. If one of them exists on the filesystem, that path is returned.

        Parameters:
            file_path (str): The Windows file path to translate.

        Returns:
            str: The translated Linux file path, or the original path if no conversion is applicable.
        """
        # Normalize the file path by replacing backslashes with forward slashes
        file_path = file_path.replace("\\", "/")

        # Check for WSL paths (e.g., "\\wsl.localhost\Ubuntu\home\user")
        if file_path.startswith("//wsl.localhost/") or file_path.startswith(
            "\\\\wsl.localhost\\"
        ):
            parts = file_path.split("/")
            if len(parts) > 4:
                return "/" + "/".join(parts[4:])
            else:
                print("Unsupported WSL distribution or incorrect path format.")

        # Check if the path is a Windows drive path (e.g., "C:\...")
        if len(file_path) > 1 and file_path[1] == ":":
            drive_letter = file_path[0].upper()
            converted_files = []

            # Loop through each mapping (Drives and Mnt)
            for mapping in self.drive_mappings.values():
                if drive_letter in mapping:
                    value = mapping[drive_letter]
                    # Create an alternative variant of the mapping
                    parts = value.split("/")
                    if len(parts) >= 2:
                        # For example, converts '/Drives/c' to '/Drives/C'
                        value_2 = f"/{os.path.join(parts[1], parts[-1].upper())}"
                    else:
                        value_2 = value
                    # Construct two potential Linux file paths
                    file_path_1 = f"{value}{file_path[2:]}"
                    file_path_2 = f"{value_2}{file_path[2:]}"
                    converted_files.extend([file_path_1, file_path_2])

            # Return the first converted file that exists on the filesystem
            for converted_file in converted_files:
                if os.path.exists(converted_file):
                    return converted_file

        # Return the original file_path if no translation was applied
        return file_path
