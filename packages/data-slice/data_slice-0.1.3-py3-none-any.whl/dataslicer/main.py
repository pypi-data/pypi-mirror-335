import os
import re
from typing import Any, Union

import pandas as pd


def sanitize_filename(filename: str) -> str:
    r"""
    Remove characters that are illegal in filenames on Windows, Mac, and Linux.
    Illegal characters include: \ / : * ? " < > |
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def get_file_path() -> str:
    """Ask the user for the file path until a valid file is provided."""
    while True:
        file_path: str = input("Enter the path to your Excel or CSV file: ").strip()
        if os.path.isfile(file_path):
            return file_path
        else:
            print("File does not exist. Please try again.")


def read_file(file_path: str) -> pd.DataFrame:
    """Read the file as a CSV or the first sheet of an Excel file."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif ext.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path, sheet_name=0)
    else:
        raise ValueError("Unsupported file type. Please provide a CSV or Excel file.")
    return df


def choose_columns(columns: list[str]) -> list[str]:
    """
    Let the user select columns by number.
    The selection order will determine the folder hierarchy.
    """
    selected_columns: list[str] = []
    available: list[str] = list(columns)  # copy of the list to show available columns

    while True:
        choice: str = input("Select a column by number (or press Enter to finish): ").strip()
        if choice == "":
            if len(selected_columns) == 0:
                print("You must select at least one column.")
                continue
            else:
                break
        try:
            num: int = int(choice)
            if num < 1 or num > len(available):
                print("Invalid selection. Try again.")
                continue
            selected_col: str = available.pop(num - 1)
            selected_columns.append(selected_col)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    return selected_columns


def get_export_folder() -> str:
    """
    Keep asking for an export folder until a valid path is provided.
    If the folder doesn't exist, try to create it.
    """
    while True:
        folder: str = input("Enter the path to the export folder: ").strip()
        if folder:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                    print(f"Folder '{folder}' created.")
                except Exception as e:
                    print(f"Could not create folder: {e}")
                    continue
            return folder
        else:
            print("You must enter a valid folder path.")


def choose_export_format() -> str:
    """
    Ask the user to choose an export format by number:
    1. Excel
    2. CSV
    """
    while True:
        print("Choose export format:")
        print("1. Excel")
        print("2. CSV")
        choice: str = input("Enter the number of the export format: ").strip()
        if choice == "1":
            return "excel"
        elif choice == "2":
            return "csv"
        else:
            print("Invalid selection. Please enter 1 or 2.")


def save_group(
    df: pd.DataFrame,
    group_keys: Union[Any, tuple[Any, ...]],
    selected_columns: list[str],
    export_folder: str,
    export_format: str,
) -> None:
    """
    Create the nested folder structure based on group_keys and save the subset file.
    The output filename is built from the group key values (in reverse order)
    joined by " - ". For example, if group_keys is (test_value, building_value),
    the filename will be "building_value - test_value" (plus the file extension).
    """
    subfolder_path: str = export_folder
    # Build the folder structure in the order of grouping (not reversed)
    if not isinstance(group_keys, tuple):
        group_keys = (group_keys,)
    for key in group_keys:
        subfolder_path = os.path.join(subfolder_path, str(key))
    os.makedirs(subfolder_path, exist_ok=True)

    # Ensure group_keys is a tuple for consistency
    if not isinstance(group_keys, tuple):
        group_keys = (group_keys,)

    # Build the filename from only the group key values in reverse order.
    filename_parts: list[str] = []
    for val in reversed(group_keys):
        filename_parts.append(str(val))
    raw_filename: str = " - ".join(filename_parts)

    # Sanitize the filename to remove illegal characters.
    sanitized_filename: str = sanitize_filename(raw_filename)

    # Append the file extension
    file_extension: str = ".xlsx" if export_format == "excel" else ".csv"
    file_name: str = sanitized_filename + file_extension
    file_path: str = os.path.join(subfolder_path, file_name)

    # Save the file in the chosen format
    if export_format == "excel":
        df.to_excel(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)
    print(f"Saved group {group_keys} to {file_path}")


def main() -> None:
    # Get the input file and load it into a DataFrame
    file_path: str = get_file_path()
    df: pd.DataFrame = read_file(file_path)

    # Display the available columns
    print("\nColumns in the file:")
    for i, col in enumerate(df.columns, start=1):
        print(f"{i}. {col}")

    # Let the user choose the columns (in order) for splitting
    split_columns: list[str] = choose_columns(df.columns.tolist())
    print("\nSelected columns (in order):", split_columns)

    # Ask for export folder and export format
    export_folder: str = get_export_folder()
    export_format: str = choose_export_format()

    # Group the DataFrame by the selected columns and export each group to its respective folder
    grouped = df.groupby(split_columns)
    print("\nSplitting file and exporting groups...")
    for group_keys, group_df in grouped:
        save_group(group_df, group_keys, split_columns, export_folder, export_format)

    print("All groups exported.")


if __name__ == "__main__":
    main()
