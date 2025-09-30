import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Dashboard Cambial", page_icon="💱", layout="wide")
st.title("💱 Dashboard de Cotações Cambiais com LLM")
st.markdown("Pipeline **raw → silver → gold** com enriquecimento via LLM.")

# ============================
# Configuração GitHub
# ============================
GITHUB_USER = "<seu-usuario>"
REPO_NAME = "<seu-repositorio>"
BRANCH = "dashboard-data"
GOLD_DIR = "data/gold"

# Lista arquivos da branch usando API GitHub
url_api = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
r = requests.get(url_api)
r.raise_for_status()
tree = r.json()["tree"]

gold_files = [
    f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{f['path']}"
    for f in tree
    if f['path'].startswith(GOLD_DIR) and f['path'].endswith(".parquet")
]

insight_files = [
    f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{f['path']}"
    for f in tree
    if f['path'].startswith(GOLD_DIR) and f['path'].endswith(".json")
]

# ============================
# Carregar e concatenar dados Parquet
# ============================
if gold_files:
    df_list = [pd.read_parquet(f) for f in gold_files]
    df = pd.concat(df_list, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])

    st.subheader("📊 Dados processados (Parquet)")
    st.dataframe(df.head())

    st.line_chart(df.set_index("date").select_dtypes("number"))
else:
    st.warning("Nenhum arquivo Parquet encontrado na branch.")

# ============================
# Insights do LLM
# ============================
if insight_files:
    st.subheader("🤖 Insights do LLM")
    all_insights = {}
    for f_url in insight_files:
        r = requests.get(f_url)
        r.raise_for_status()
        data = r.json()
        all_insights.update(data)
    st.json(all_insights)
else:
    st.info("Nenhum arquivo de insights do LLM encontrado na branch.")

# ============================
# Filtros interativos
# ============================
if gold_files:
    st.sidebar.header("Filtros")
    moedas = [c for c in df.columns if c not in ["date"]]
    moeda = st.sidebar.selectbox("Escolha uma moeda:", moedas)

    st.subheader(f"📈 Evolução da moeda: {moeda}")
    st.line_chart(df.set_index("date")[moeda])
