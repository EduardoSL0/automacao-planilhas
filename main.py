import pandas as pd
import os

# =========================
# CAMINHOS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_EXCEL = os.path.join(BASE_DIR, "entrada.xlsx")
PASTA_OUTPUT = os.path.join(BASE_DIR, "output")

os.makedirs(PASTA_OUTPUT, exist_ok=True)

# =========================
# FUNÇÃO CPF
# =========================
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, str(cpf)))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito
        if digito != int(cpf[i]):
            return False

    return True

# =========================
# VERIFICAR ARQUIVO
# =========================
if not os.path.exists(ARQUIVO_EXCEL):
    print("❌ ERRO: entrada.xlsx não encontrado")
    print(f"📂 Caminho esperado: {ARQUIVO_EXCEL}")
    exit()

# =========================
# LER PLANILHA
# =========================
df = pd.read_excel(ARQUIVO_EXCEL)

# =========================
# NORMALIZAR COLUNAS
# =========================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
    .str.replace("r$", "")
    .str.replace("$", "")
    .str.replace("á", "a")
    .str.replace("ã", "a")
    .str.replace("â", "a")
    .str.replace("é", "e")
    .str.replace("í", "i")
    .str.replace("ó", "o")
    .str.replace("ú", "u")
    .str.replace("ç", "c")
)

print("📌 Colunas encontradas:", df.columns.tolist())

# =========================
# COLUNA DE ERRO
# =========================
df["erro"] = ""

# =========================
# VALIDAÇÕES
# =========================
for index, row in df.iterrows():
    erros = []

    if pd.isna(row["nome"]) or str(row["nome"]).strip() == "":
        erros.append("Nome vazio")

    if pd.isna(row["email"]) or str(row["email"]).strip() == "":
        erros.append("Email vazio")

    if not validar_cpf(row["cpf"]):
        erros.append("CPF inválido")

    if row["salario_"] <= 0:
        erros.append("Salário inválido")

    if row["gasto_medio_diario_"] <= 0:
        erros.append("Gasto diário inválido")

    df.at[index, "erro"] = ", ".join(erros)

# =========================
# ANÁLISE FINANCEIRA
# =========================
df["gasto_mensal_estimado"] = df["gasto_medio_diario_"] * 30
df["percentual_gasto_salario"] = (
    df["gasto_mensal_estimado"] / df["salario_"]
) * 100

# =========================
# SEPARAR DADOS
# =========================
dados_validos = df[df["erro"] == ""]
dados_invalidos = df[df["erro"] != ""]

# =========================
# SALVAR RESULTADOS
# =========================
dados_validos.drop(columns=["erro"]).to_excel(
    os.path.join(PASTA_OUTPUT, "dados_validos.xlsx"),
    index=False
)

dados_invalidos.to_excel(
    os.path.join(PASTA_OUTPUT, "relatorio_erros.xlsx"),
    index=False
)

# =========================
# RESUMO FINAL
# =========================
print("\n✅ Processamento finalizado com sucesso!")
print(f"📊 Total de registros: {len(df)}")
print(f"✔ Registros válidos: {len(dados_validos)}")
print(f"❌ Registros com erro: {len(dados_invalidos)}")
print("📁 Arquivos gerados na pasta: output")
