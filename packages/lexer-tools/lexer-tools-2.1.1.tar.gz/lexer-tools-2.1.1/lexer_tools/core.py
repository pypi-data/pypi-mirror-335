import os
import shutil

def save_files(output_dir):
    """
    Copies files from all folders (exp1, exp2, exp3, exp4, exp5) in the package's data directory
    to the output directory.

    Args:
        output_dir (str): Path to the local directory where files will be saved.
    """
    # Get the path to the package's data directory
    package_dir = os.path.dirname(__file__)
    data_dir = os.path.join(package_dir, "data")

    # List of folders to copy
    folders = ["exp1", "exp2", "exp3", "exp4", "exp5"]

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Copy files from each folder to the output directory
    for folder in folders:
        folder_path = os.path.join(data_dir, folder)

        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"Warning: Folder '{folder}' not found in the package's data directory.")
            continue

        # Copy each file in the folder
        for file_name in os.listdir(folder_path):
            src_file = os.path.join(folder_path, file_name)
            dest_file = os.path.join(output_dir, file_name)
            shutil.copy(src_file, dest_file)
            print(f"Copied {file_name} from {folder} to {output_dir}")