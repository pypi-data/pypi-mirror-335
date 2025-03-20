import pandas as pd

def _check_dtype(series, expected_type):
    """
    🎯 Verifica se a série possui o tipo de dado esperado.
    - Aceita floats inteiros como válidos para int.
    - Lida com valores nulos.
    """
    try:
        if expected_type == int:
            return series.dropna().apply(lambda x: float(x).is_integer()).all()
        elif expected_type == float:
            return series.dropna().apply(lambda x: isinstance(x, (float, int))).all()
        elif expected_type == str:
            return series.dropna().apply(lambda x: isinstance(x, str)).all()
        else:
            return series.dropna().apply(lambda x: isinstance(x, expected_type)).all()
    except Exception:
        return False


def validate_excel_schema(file_path, schema, sheet_name=None):
    """
    🛡️ Valida se um arquivo Excel segue o esquema especificado.

    Args:
        file_path (str): Caminho para o arquivo Excel.
        schema (dict): Dicionário com o nome da coluna e o tipo esperado. Ex.: {"Nome": str, "Idade": int}
        sheet_name (str ou None): Nome da planilha. Se None, lê a primeira.

    Returns:
        dict: {
            "valid": bool,
            "errors": list (se houver)
        }
    """
    resultado = {"valid": True, "errors": []}

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # ✅ Força leitura da primeira planilha se múltiplas forem retornadas
        if isinstance(df, dict):
            df = list(df.values())[0]

        # 🚨 Verificar se todas as colunas existem e validar tipos
        for coluna, tipo in schema.items():
            if coluna not in df.columns:
                resultado["valid"] = False
                resultado["errors"].append(f"❌ Coluna ausente: '{coluna}'")
            else:
                # 🎯 Validação robusta de tipo
                if not _check_dtype(df[coluna], tipo):
                    resultado["valid"] = False
                    resultado["errors"].append(f"⚠️ Coluna '{coluna}' com tipo inválido. Esperado: {tipo.__name__}")

    except Exception as e:
        resultado["valid"] = False
        resultado["errors"].append(f"❌ Erro ao validar esquema: {str(e)}")

    return resultado


# 🌟 Exemplo de uso
if __name__ == "__main__":
    schema = {"Nome": str, "Idade": int, "Salario": float}
    resultado = validate_excel_schema("dados.xlsx", schema)
    if resultado["valid"]:
        print("✅ Validação bem-sucedida!")
    else:
        print("❌ Validação falhou:")
        for erro in resultado["errors"]:
            print(" -", erro)
