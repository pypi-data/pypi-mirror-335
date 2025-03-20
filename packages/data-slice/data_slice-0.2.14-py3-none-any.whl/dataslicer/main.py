import os
from typing import Any, Union

import pandas as pd
from pathvalidate import sanitize_filename, sanitize_filepath
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def get_file_path() -> str:
    """Ask the user for the file path until a valid file is provided."""
    while True:
        file_path: str = Prompt.ask("[bold cyan]Enter the path to your Excel or CSV file[/]").strip()
        if os.path.isfile(file_path):
            return file_path
        else:
            console.print("[bold red]File does not exist. Please try again.[/]")


def read_file(file_path: str) -> pd.DataFrame:
    """Read the file as a CSV or the first sheet of an Excel file."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif ext.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path, sheet_name=0)
    else:
        raise ValueError("[bold red]Unsupported file type. Please provide a CSV or Excel file.[/]")
    return df


def choose_columns(columns: list[str]) -> list[str]:
    """
    Let the user select columns by number.
    The selection order will determine the folder hierarchy.
    """
    selected_columns: list[str] = []
    available: list[str] = list(columns)  # Copy of the list to show available columns

    while True:
        table = Table(title="Available columns to split by (order matters)", show_lines=True)
        table.add_column("#", justify="right", style="bold")
        table.add_column("Column Name", style="cyan")

        for i, col in enumerate(available, start=1):
            table.add_row(str(i), col)

        console.print(table)
        choice: str = Prompt.ask("[bold yellow]Select a column by number (or press Enter to finish)[/]").strip()

        if choice == "":
            if not selected_columns:
                console.print("[bold red]You must select at least one column.[/]")
                continue
            else:
                break
        try:
            num: int = int(choice)
            if num < 1 or num > len(available):
                console.print("[bold red]Invalid selection. Try again.[/]")
                continue
            selected_col: str = available.pop(num - 1)
            selected_columns.append(selected_col)
        except ValueError:
            console.print("[bold red]Invalid input. Please enter a valid number.[/]")

    return selected_columns


def get_export_folder() -> str:
    """
    Keep asking for an export folder until a valid path is provided.
    If the folder doesn't exist, try to create it.
    """
    while True:
        folder: str = Prompt.ask("[bold cyan]Enter the path to the export folder[/]").strip()
        if folder:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                    console.print(f"[bold green]Folder '{folder}' created.[/]")
                except Exception as e:
                    console.print(f"[bold red]Could not create folder: {e}[/]")
                    continue
            return folder
        else:
            console.print("[bold red]You must enter a valid folder path.[/]")


def choose_export_format() -> str:
    """
    Ask the user to choose an export format by number:
    1. Excel
    2. CSV
    """
    console.print("\n[bold yellow]Choose export format:[/]")
    console.print("[bold]1.[/] Excel")
    console.print("[bold]2.[/] CSV")

    while True:
        choice: str = Prompt.ask("[bold cyan]Enter the number of the export format[/]").strip()
        if choice == "1":
            return "excel"
        elif choice == "2":
            return "csv"
        else:
            console.print("[bold red]Invalid selection. Please enter 1 or 2.[/]")


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
        subfolder_path = sanitize_filepath(os.path.join(subfolder_path, sanitize_filename(key)))
    os.makedirs(subfolder_path, exist_ok=True)

    # Build the filename from only the group key values in reverse order.
    filename_parts: list[str] = [str(val) for val in reversed(group_keys)]
    raw_filename: str = " - ".join(filename_parts)

    # Sanitize the filename
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

    console.print(f"[bold green]Saved group {group_keys} to {file_path}[/]")


def main() -> None:
    console.print("[bold cyan]Welcome to the File Splitter![/]")

    # Get the input file and load it into a DataFrame
    file_path: str = get_file_path()
    df: pd.DataFrame = read_file(file_path)

    # Display the available columns
    console.print("\n[bold cyan]Columns in the file:[/]")
    table = Table(title="Available Columns", show_lines=True)
    table.add_column("#", justify="right", style="bold")
    table.add_column("Column Name", style="cyan")

    for i, col in enumerate(df.columns, start=1):
        table.add_row(str(i), col)

    console.print(table)

    # Let the user choose the columns (in order) for splitting
    split_columns: list[str] = choose_columns(df.columns.tolist())
    console.print("\n[bold yellow]Selected columns (in order):[/]", split_columns)

    # Ask for export folder and export format
    export_folder: str = get_export_folder()
    export_format: str = choose_export_format()

    # Group the DataFrame by the selected columns and export each group
    grouped = df.groupby(split_columns)
    console.print("\n[bold cyan]Splitting file and exporting groups...[/]")
    for group_keys, group_df in grouped:
        save_group(group_df, group_keys, split_columns, export_folder, export_format)

    console.print("[bold green]All groups exported successfully![/]")


if __name__ == "__main__":
    main()
