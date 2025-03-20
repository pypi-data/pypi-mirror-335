import pandas as pd


def read_excel(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    """
    📥 Lê um arquivo Excel e retorna um DataFrame.

    Args:
        file_path (str): Caminho do arquivo Excel.
        sheet_name (str, opcional): Nome da planilha. Se None, lê a primeira.

    Returns:
        pd.DataFrame: Dados da planilha em formato DataFrame.
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"❌ Erro ao ler o arquivo {file_path}: {str(e)}")


def read_csv(file_path: str) -> pd.DataFrame:
    """
    📥 Lê um arquivo CSV e retorna um DataFrame.

    Args:
        file_path (str): Caminho do arquivo CSV.

    Returns:
        pd.DataFrame: Dados do CSV em formato DataFrame.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"❌ Erro ao ler o arquivo CSV {file_path}: {str(e)}")