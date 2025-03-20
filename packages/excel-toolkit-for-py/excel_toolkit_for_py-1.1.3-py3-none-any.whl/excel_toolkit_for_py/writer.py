import pandas as pd


def write_excel(dataframe: pd.DataFrame, file_path: str, sheet_name: str = "Sheet1") -> None:
    """
    📤 Exporta um DataFrame para um arquivo Excel.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser exportado.
        file_path (str): Caminho de saída do arquivo Excel.
        sheet_name (str): Nome da planilha.
    """
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        raise ValueError(f"❌ Erro ao exportar o DataFrame para {file_path}: {str(e)}")


def write_csv(dataframe: pd.DataFrame, file_path: str) -> None:
    """
    📤 Exporta um DataFrame para um arquivo CSV.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser exportado.
        file_path (str): Caminho de saída do arquivo CSV.
    """
    try:
        dataframe.to_csv(file_path, index=False)
    except Exception as e:
        raise ValueError(f"❌ Erro ao exportar o DataFrame para CSV {file_path}: {str(e)}")
