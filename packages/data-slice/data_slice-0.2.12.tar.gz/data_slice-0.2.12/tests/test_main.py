import os

import pandas as pd
import pytest

from dataslicer.main import (
    choose_columns,
    choose_export_format,
    get_export_folder,
    get_file_path,
    read_file,
    sanitize_for_filesystem,  # Updated import
    save_group,
)

TEST_CSV_CONTENT = """Name,Department,Salary
Alice,HR,50000
Bob,IT,60000
Charlie,HR,55000
David,IT,70000
"""

TEST_DF = pd.DataFrame(
    {
        "Name": ["Alice", "Bob", "Charlie", "David"],
        "Department": ["HR", "IT", "HR", "IT"],
        "Salary": [50000, 60000, 55000, 70000],
    }
)


@pytest.fixture
def temp_csv(tmp_path):
    """Creates a temporary CSV file."""
    temp_file = tmp_path / "test_file.csv"
    temp_file.write_text(TEST_CSV_CONTENT)
    return str(temp_file)


def test_sanitize_for_filesystem():
    """Test that filenames and folder names are correctly sanitized."""
    # Test file sanitization (is_folder=False)
    assert sanitize_for_filesystem("valid_filename") == "valid_filename"
    assert sanitize_for_filesystem("inva|lid:na*me?.txt") == "inva_lid_na_me_.txt"
    assert sanitize_for_filesystem("normal-file.txt") == "normal-file.txt"
    assert sanitize_for_filesystem("path/with/slashes.txt") == "path_with_slashes.txt"

    # Test folder sanitization (is_folder=True)
    assert sanitize_for_filesystem("valid_folder", is_folder=True) == "valid_folder"
    assert sanitize_for_filesystem("inva|lid:fo*lder?", is_folder=True) == "inva_lid_fo_lder_"
    assert sanitize_for_filesystem("path/with/slashes", is_folder=True) == "path/with/slashes"
    assert sanitize_for_filesystem("folder\\with:bad*chars", is_folder=True) == "folder_with_bad_chars"


def test_get_file_path(temp_csv, monkeypatch):
    """Test get_file_path() with a valid file."""
    monkeypatch.setattr("builtins.input", lambda *args: temp_csv)
    assert get_file_path() == temp_csv


def test_read_file_csv(temp_csv):
    """Test reading a CSV file."""
    df = read_file(temp_csv)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Name", "Department", "Salary"]
    assert len(df) == 4  # Four rows in test data


def test_choose_columns(monkeypatch):
    """Test column selection function."""
    inputs = iter(["1", "1", ""])  # Select columns 1 and 2, then press Enter
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    selected_columns = choose_columns(["Name", "Department", "Salary"])
    assert selected_columns == ["Name", "Department"]


def test_get_export_folder(monkeypatch, tmp_path):
    """Test getting an export folder."""
    temp_folder = str(tmp_path / "export")
    monkeypatch.setattr("builtins.input", lambda *args: temp_folder)
    assert get_export_folder() == temp_folder


def test_choose_export_format(monkeypatch):
    """Test export format selection."""
    monkeypatch.setattr("builtins.input", lambda *args: "1")  # User selects Excel
    assert choose_export_format() == "excel"

    monkeypatch.setattr("builtins.input", lambda *args: "2")  # User selects CSV
    assert choose_export_format() == "csv"


def test_save_group(tmp_path):
    """Test that the grouped data is saved correctly."""
    export_folder = tmp_path / "exports"
    os.makedirs(export_folder, exist_ok=True)

    save_group(
        df=TEST_DF,
        group_keys=("HR",),
        selected_columns=["Department"],
        export_folder=str(export_folder),
        export_format="csv",
    )

    expected_file = export_folder / "HR" / "HR.csv"
    assert expected_file.exists(), f"Expected file {expected_file} does not exist."


def test_save_group_with_special_chars(tmp_path):
    """Test that special characters in folder/file names are handled correctly."""
    export_folder = tmp_path / "exports"
    os.makedirs(export_folder, exist_ok=True)

    save_group(
        df=TEST_DF,
        group_keys=("HR/Dept1",),
        selected_columns=["Department"],
        export_folder=str(export_folder),
        export_format="csv",
    )

    expected_file = export_folder / "HR/Dept1" / "HR_Dept1.csv"
    assert expected_file.exists(), f"Expected file {expected_file} does not exist."


@pytest.fixture
def mock_grouped_data():
    """Mock grouped data for testing."""
    grouped = TEST_DF.groupby("Department")
    return grouped


def test_grouping_and_saving(mock_grouped_data, tmp_path):
    """Test full flow of grouping and saving data."""
    export_folder = tmp_path / "exports"
    os.makedirs(export_folder, exist_ok=True)

    for group_keys, group_df in mock_grouped_data:
        save_group(
            df=group_df,
            group_keys=group_keys,
            selected_columns=["Department"],
            export_folder=str(export_folder),
            export_format="csv",
        )

    for department in ["HR", "IT"]:
        expected_file = export_folder / department / f"{department}.csv"
        assert expected_file.exists(), f"Expected file {expected_file} does not exist."
