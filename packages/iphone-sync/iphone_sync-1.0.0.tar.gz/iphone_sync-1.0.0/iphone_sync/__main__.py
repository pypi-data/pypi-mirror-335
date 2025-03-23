import argparse
import os
from pathlib import Path
from typing import Any
from typing import cast

import win32com.client
from tqdm import tqdm


def copy_files_from_iphone(destination_folder: Path):
    shell = win32com.client.Dispatch("Shell.Application")

    # Step 1: Get "This PC"
    my_computer = shell.Namespace(17)  # CLSID for "This PC"

    # Step 2: Find the iPhone
    iphone = None
    for item in my_computer.Items():
        if "iPhone" in item.Name:
            iphone = item
            break
    else:
        print("iPhone not found.")
        return

    # Step 3: Open iPhone Storage
    iphone_folder = iphone.GetFolder  # Get internal storage
    if not iphone_folder:
        print("Unable to access iPhone storage.")
        return

    # Step 4: Find and Open "Internal Storage"
    internal_storage = None
    for item in iphone_folder.Items():
        if "Internal Storage" in item.Name:
            internal_storage = item.GetFolder
            break
    else:
        print("Internal Storage not found.")
        return

    # Step 5: List all files inside "Internal Storage"
    print("🔍 Scanning files from your iPhone...")
    to_copy: list[tuple[Any, str, Any, str]] = []
    for subfolder in internal_storage.Items():
        subfolder_name = cast(str, subfolder.Name)
        subfolder_obj = subfolder.GetFolder
        exist_count = 0
        total_count = 0
        for file_obj in subfolder_obj.Items():
            file_name = cast(str, file_obj.Name)
            exists = (destination_folder / subfolder_name / file_name).exists()
            total_count += 1
            if exists:
                exist_count += 1
            else:
                to_copy.append(
                    (subfolder_obj, subfolder_name, file_obj, file_name)
                )
        synced = exist_count >= total_count
        icon = "✅ Sycned" if synced else "❌ Out of Sync"
        print(f"📁 {subfolder_name} - {icon} - ({exist_count}/{total_count})")

    # Step 6: Copy the files to destination
    if to_copy:
        pbar = tqdm(to_copy)
        for subfolder_obj, subfolder_name, file_obj, file_name in pbar:
            pbar.set_description(f"💾 {subfolder_name}/{file_name}")
            os.makedirs(destination_folder / subfolder_name, exist_ok=True)
            destination = shell.Namespace(
                str(destination_folder / subfolder_name)
            )
            destination.CopyHere(file_obj)
    print("✅ All Done!")


def main():

    # Initialize the parser
    parser = argparse.ArgumentParser(
        description="Parse destination folder argument"
    )

    # Add the destination folder argument
    parser.add_argument(
        "destination_folder", type=str, help="The destination folder path"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Access the destination folder
    destination_folder = args.destination_folder

    copy_files_from_iphone(Path(destination_folder).absolute())


if __name__ == "__main__":
    main()
