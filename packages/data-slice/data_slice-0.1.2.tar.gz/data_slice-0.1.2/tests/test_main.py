import os

import pandas as pd
import pytest

from dataslicer.main import (
    choose_columns,
    choose_export_format,
    get_export_folder,
    read_file,
    sanitize_filename,
    save_group,
)


def test_sanitize_filename():
    # Provide a string with illegal filename characters.
    input_str = 'test:/file*name?"<>|'
    expected = "testfilename"  # all illegal characters are removed
    assert sanitize_filename(input_str) == expected


def test_read_file_csv(tmp_path):
    # Create a temporary CSV file.
    csv_content = "a,b\n1,2\n3,4\n"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    # Read the file using the read_file function.
    df = read_file(str(csv_file))
    assert list(df.columns) == ["a", "b"]
    assert df.shape[0] == 2


def test_choose_columns(monkeypatch):
    # Simulate user inputs:
    # "1" selects the first available column,
    # "1" selects the first of the remaining columns,
    # and then an empty string to finish.
    inputs = iter(["1", "1", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    available_columns = ["a", "b", "c"]
    result = choose_columns(available_columns)
    # The first input ("1") selects "a", then list becomes ["b", "c"];
    # second input ("1") selects "b"; then "" ends the loop.
    assert result == ["a", "b"]


@pytest.mark.parametrize("user_input,expected", [(["1"], "excel"), (["2"], "csv")])
def test_choose_export_format(monkeypatch, user_input, expected):
    inputs = iter(user_input)
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = choose_export_format()
    assert result == expected


def test_save_group(tmp_path):
    # Create a dummy DataFrame.
    df = pd.DataFrame({"col": [1, 2, 3]})
    # Define group_keys as a tuple.
    group_keys = ("Test", "Building")
    # Use a temporary export folder.
    export_folder = str(tmp_path / "export")
    export_format = "csv"

    # Call save_group which should create a nested folder structure and a file.
    save_group(df, group_keys, selected_columns=["dummy"], export_folder=export_folder, export_format=export_format)

    # The folder structure created is: export_folder / "Test" / "Building"
    folder_path = os.path.join(export_folder, "Test", "Building")
    # The filename is built from reversed group_keys: "Building - Test.csv"
    expected_filename = "Building - Test.csv"
    file_path = os.path.join(folder_path, expected_filename)
    assert os.path.isfile(file_path)


def test_get_export_folder(monkeypatch, tmp_path):
    # Provide a folder path that does not exist.
    folder_path = str(tmp_path / "new_export_folder")
    inputs = iter([folder_path])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    result = get_export_folder()
    # The folder should now exist.
    assert os.path.isdir(result)
    assert result == folder_path
