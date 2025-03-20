# 📚 **excel-toolkit-for-py - Manipulação e Conversão Avançada de Arquivos Excel**

📊 **excel-toolkit-for-py** é um pacote Python completo que facilita a **leitura, manipulação, validação e conversão de arquivos Excel e CSV**, utilizando `pandas` e `openpyxl`. Ideal para automações robustas envolvendo planilhas!

---

## ✨ **Principais Funcionalidades**

- 📥 **Leitura de arquivos Excel (`.xlsx`) e CSV (`.csv`).**
- 📤 **Exportação de DataFrames para Excel e CSV.**
- 🔄 **Conversão entre Excel e JSON.**
- 🔗 **Junção e divisão de arquivos Excel.**
- 🛡️ **Validações automatizadas de dados e esquemas.**
- 📊 **Suporte a múltiplas planilhas.**
- ✅ **Integração com `pytest` para testes automatizados.**

---

## ⚡ **Instalação**

Instale o pacote via **PyPI**:

```bash
pip install excel_toolkit_for_py
```

> 💡 As dependências `pandas` e `openpyxl` são instaladas automaticamente.

---

## 🚀 **Como Usar**

### 📥 **Leitura de Arquivos Excel e CSV**

```python
from excel_toolkit_for_py.reader import read_excel, read_csv

# Lendo um arquivo Excel
df_excel = read_excel("dados.xlsx", sheet_name="Sheet1")
print(df_excel.head())

# Lendo um arquivo CSV
df_csv = read_csv("dados.csv")
print(df_csv.head())
```

---

### 📤 **Exportação de DataFrames para Excel e CSV**

```python
from excel_toolkit_for_py.writer import write_excel, write_csv
import pandas as pd

df = pd.DataFrame({
    "Nome": ["Alice", "Bob", "Carlos"],
    "Idade": [25, 30, 22]
})

write_excel(df, "saida.xlsx", sheet_name="Usuarios")
write_csv(df, "saida.csv")
```

---

### 🔄 **Conversão: Excel para JSON e vice-versa**

```python
from excel_toolkit_for_py.conversions import excel_to_json, json_to_excel

# Excel -> JSON
json_data = excel_to_json("dados.xlsx")
print(json_data)

# JSON -> Excel
json_to_excel(json_data, "novo_dados.xlsx")
```

---

### 🛡️ **Validação de Estrutura e Dados**

```python
from excel_toolkit_for_py.validations import validate_excel_schema

schema = {"Nome": str, "Idade": int}
validacao = validate_excel_schema("dados.xlsx", schema)
print("✅ Validação bem-sucedida!" if validacao else "❌ Validação falhou.")
```

---

## 🧪 **Testes**

Execute os testes unitários com **pytest**:

```bash
pytest tests/ --maxfail=1 --disable-warnings -v
```

---

## 🏗 **Estrutura do Projeto**

```
excel_toolkit/
│
├── excel_toolkit_for_py/                # 📦 Código do pacote
│   ├── __init__.py
│   ├── reader.py            # 📥 Funções de leitura
│   ├── writer.py            # 📤 Funções de exportação
│   ├── conversions.py       # 🔄 Funções de conversão Excel <-> JSON
│   ├── validations.py       # 🛡️ Funções de validação de dados
│
├── tests/                   # 🧪 Testes unitários
│   ├── test_reader.py
│   ├── test_writer.py
│   ├── test_conversions.py
│   ├── test_validations.py
│
├── setup.py                 # ⚙️ Configuração para PyPI
├── pyproject.toml           # 📦 Configuração moderna
├── README.md                # 📚 Documentação do projeto
├── LICENSE                  # 📜 Licença MIT
└── MANIFEST.in              # 📋 Inclusão de arquivos extras
```

---

## 📝 **Licença**

Distribuído sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 **Autor**

Desenvolvido por **[Roberto Lima](https://robertolima-developer.vercel.app/)** 🚀✨

---

## 💬 **Contato**

- 📧 **Email**: robertolima.izphera@gmail.com
- 💼 **LinkedIn**: [Roberto Lima](https://www.linkedin.com/in/roberto-lima-01/)
- 💼 **Website**: [Roberto Lima](https://robertolima-developer.vercel.app/)
- 💼 **Gravatar**: [Roberto Lima](https://gravatar.com/deliciouslyautomaticf57dc92af0)

---

## ⭐ **Gostou do projeto?**

Deixe uma ⭐ no repositório e compartilhe com a comunidade! 🚀✨
