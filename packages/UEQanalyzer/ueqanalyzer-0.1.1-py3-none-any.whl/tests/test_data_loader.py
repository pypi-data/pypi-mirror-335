# tests/test_data_loader.py
import pytest
import pandas as pd
from UEQanalyzer.data_loader import load_ueq_data

def test_load_ueq_data_success():
    """Test loading a valid Excel file."""
    file_path = "ueq_data.xlsx"  
    data = load_ueq_data(file_path)
    assert isinstance(data, pd.DataFrame), "Expected a DataFrame"
    assert not data.empty, "DataFrame should not be empty"
  
def test_load_ueq_data_invalid_file():
    """Test loading an invalid file."""
    file_path = "invalid_data.txt"  
    data = load_ueq_data(file_path)
    assert data is None, "Expected None for invalid file"

