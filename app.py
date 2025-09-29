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

# Dataset principal (Parquet)
parquet_files = list(gold_path.glob("*.parquet"))
if parquet_files:
    df = pd.read_parquet(parquet_files[0])  # pega o primeiro parquet
    st.subheader("📊 Dados processados (Parquet)")
    st.dataframe(df.head())

    if "date" in df.columns:
        st.line_chart(df.set_index("date").select_dtypes("number"))

else:
    st.warning("Nenhum arquivo Parquet encontrado em /data/gold")

# Insights do LLM
insight_files = list(gold_path.glob("*insights*.json"))
if insight_files:
    st.subheader("🤖 Insights do LLM")
    with open(insight_files[0], "r", encoding="utf-8") as f:
        insights = json.load(f)
    st.json(insights)
else:
    st.info("Nenhum arquivo de insights do LLM encontrado em /data/gold")

# ============================
# Extra: filtros interativos
# ============================
if parquet_files:
    st.sidebar.header("Filtros")
    moedas = [c for c in df.columns if c not in ["date"]]
    moeda = st.sidebar.selectbox("Escolha uma moeda:", moedas)

    st.subheader(f"📈 Evolução da moeda: {moeda}")
    st.line_chart(df.set_index("date")[moeda])
