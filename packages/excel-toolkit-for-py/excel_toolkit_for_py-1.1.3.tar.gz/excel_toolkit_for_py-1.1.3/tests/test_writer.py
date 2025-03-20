import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from excel_toolkit_for_py.writer import write_excel, write_csv


def test_write_excel(tmp_path):
    """Testa a escrita de um arquivo Excel."""
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    
    write_excel(df, file_path)
    # ✅ Correção: especificar sheet_name para garantir retorno de DataFrame
    df_read = pd.read_excel(file_path, engine='openpyxl', sheet_name='Sheet1')
    
    pd.testing.assert_frame_equal(df, df_read)


def test_write_csv(tmp_path):
    """Testa a escrita de um arquivo CSV."""
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    
    write_csv(df, file_path)
    df_read = pd.read_csv(file_path)
    
    pd.testing.assert_frame_equal(df, df_read)
