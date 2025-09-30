import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Dashboard Cambial", page_icon="💱", layout="wide")

st.title("💱 Dashboard de Cotações Cambiais com LLM")
st.markdown("Pipeline **raw → silver → gold** com enriquecimento via LLM.")

# ============================
# Carregar dados do gold
# ============================
gold_path = Path("data/gold")

# Carrega todos os arquivos Parquet
parquet_files = sorted(gold_path.glob("*.parquet"))
if parquet_files:
    dfs = [pd.read_parquet(f) for f in parquet_files]
    df = pd.concat(dfs, ignore_index=True)

    # Converte a coluna date para datetime, se necessário
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    st.subheader("📊 Dados processados (Parquet)")
    st.dataframe(df.head())

    if "date" in df.columns:
        st.line_chart(df.set_index("date").select_dtypes("number"))

else:
    st.warning("Nenhum arquivo Parquet encontrado em /data/gold")

# ============================
# Carregar insights do LLM
# ============================
insight_files = sorted(gold_path.glob("*insights*.json"))
if insight_files:
    st.subheader("🤖 Insights do LLM")
    all_insights = {}
    for f in insight_files:
        with open(f, "r", encoding="utf-8") as file:
            insights = json.load(file)
            all_insights.update(insights)
    st.json(all_insights)
else:
    st.info("Nenhum arquivo de insights do LLM encontrado em /data/gold")

# ============================
# Filtros interativos
# ============================
if parquet_files:
    st.sidebar.header("Filtros")
    moedas = [c for c in df.columns if c not in ["date"]]
    if moedas:
        moeda = st.sidebar.selectbox("Escolha uma moeda:", moedas)
        st.subheader(f"📈 Evolução da moeda: {moeda}")
        st.line_chart(df.set_index("date")[moeda])
