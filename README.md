# Projeto Final – Pipeline de Cotações Cambiais com Python + LLM

Este projeto implementa um **pipeline ETL completo** para ingestão, transformação, armazenamento e enriquecimento de dados de **cotações cambiais** com uso de **LLM (ChatGPT ou similar)**.  

Faz parte do MBA em Data Engineering – disciplina *Python Programming for Data Engineers*.

---

## 📌 Funcionalidades
- Ingestão de dados da API [ExchangeRate API](https://www.exchangerate-api.com/).
- Armazenamento em camadas:
  - **Raw** → JSONs brutos (por data).
  - **Silver** → Dados normalizados e validados.
  - **Gold** → Dados finais em formato **Parquet**, prontos para análise.
- Enriquecimento com **LLM** para gerar resumos executivos em linguagem natural.
- Logging estruturado com `structlog`.
- Testes unitários com `pytest`.
- Suporte a configuração via `.env` (nunca deixar chaves hardcoded).

---

## 📂 Estrutura de Pastas

```
project/
│── src/
│   ├── ingest.py          # Ingestão da API
│   ├── transform.py       # Normalização e validação
│   ├── load.py            # Escrita em gold (Parquet)
│   ├── llm_enrich.py      # Integração com LLM (insights)
│   └── logging_config.py  # Configuração de logging
│
│── data/
│   ├── raw/               # Dados brutos
│   ├── silver/            # Dados normalizados
│   └── gold/              # Dados finais (Parquet + insights)
│
│── tests/                 # Testes unitários
│── requirements.txt
│── README.md
│── .env.example           # Exemplo de variáveis de ambiente
```

* `/data/raw/` → Dados brutos coletados da API, incluindo metadados (timestamp, status HTTP, URL).
* `/data/raw/rejects/` → Linhas rejeitadas durante a transformação, com motivo.
* `/data/silver/` → Dados transformados e validados em formato Parquet.
* `/data/gold/` → Dados finais prontos para consumo analítico e relatórios.
* `/data/gold/insights/` → Relatórios de insights gerados pelo LLM.
* `/logs/` → Logs estruturados em JSON de todas as etapas.
* `/src/` → Código do pipeline (`ingest.py`, `transform.py`, `load.py`, `llm_enrich.py`, `utils.py`).
* `/tests/` → Testes unitários e de integração.



## ⚙️ Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/exchange-rate-pipeline-llm.git
   cd exchange-rate-pipeline-llm
   ```

2. Crie um ambiente virtual e instale dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate    # Windows

   pip install -r requirements.txt
   ```

3. Configure suas variáveis de ambiente no arquivo `.env`:
   ```bash
   cp .env.example .env
   ```

   Exemplo de `.env`:
   ```
   EXCHANGE_API_KEY=chave_da_api
   EXCHANGE_BASE_URL=https://v6.exchangerate-api.com/v6
   OPENAI_API_KEY=sua_chave_openai
   DB_URI=postgresql://user:password@localhost:5432/exchange_db
   SIMULATE_LLM=true
   ```

   - **SIMULATE_LLM**: se `true`, não chama o OpenAI de fato (modo simulação).

---

## ▶️ Execução do Pipeline

1. **Ingestão** (salva JSON em `data/raw/`):
   ```bash
   python src/ingest.py
   ```

2. **Transformação** (gera `data/silver/`):
   ```bash
   python src/transform.py
   ```

3. **Carga** (gera Parquet em `data/gold/`):
   ```bash
   python src/load.py
   ```

4. **Enriquecimento com LLM** (gera insights em `data/gold/YYYY-MM-DD-insights.txt`):
   ```bash
   python src/llm_enrich.py
   ```

---

## 🧪 Testes

Rodar testes unitários:
```bash
pytest -q
```

---


## 📊 Outputs Esperados

- `data/gold/*.parquet` → dados finais limpos.
- `data/gold/YYYY-MM-DD-insights.txt` → insights em linguagem natural gerados pela LLM.

Exemplo de insight:
```
Em relação ao Real hoje:
- O Dólar está estável comparado ao mês passado.
- O Euro apresenta leve valorização (+3%).
- O Iene mostra alta volatilidade.
```

---

## ▶️ Executando o pipeline

### 🟢 Ingestão

```bash
python src/ingest.py --date YYYY-MM-DD
```

- Salva JSON bruto em `/data/raw/YYYY-MM-DD.json`.  
- Se houver mais de uma coleta no dia: `/data/raw/YYYY-MM-DD_HHMMSS.json`.  
- Inclui metadados: **timestamp, status HTTP, URL**.  
- Logs estruturados em JSON em `/logs/`.  

---

### 🔵 Transformação

```bash
python src/transform.py --date YYYY-MM-DD
```

- Lê JSON bruto correspondente à data.  
- Normaliza em DataFrame com colunas obrigatórias:  
  - `base_currency` (string)  
  - `target_currency` (string)  
  - `rate` (float, arredondado 6 casas)  
  - `retrieved_at` (timestamp ISO)  
  - `date` (YYYY-MM-DD)  
- Valida taxas (**não nulas, não zero, não negativas**).  
- Remove duplicatas (`target_currency` + `retrieved_at`).  
- Linhas inválidas vão para `/data/raw/rejects/` com motivo.  
- Resultado limpo gravado em `/data/silver/YYYY-MM-DD.parquet`.  

---

### 🟣 Carga final

```bash
python src/load.py --date YYYY-MM-DD
```

- Agrega arquivos em `/data/silver/`.  
- Gera artefato final `/data/gold/YYYY-MM-DD.parquet`.  
- Inclui metadados: `run_id` (UUID), `pipeline_version`, `timestamp`.  
- Garantia de índice único (`date + base_currency + target_currency`) para evitar duplicatas.  
- Pode gravar em banco relacional via **SQLAlchemy**.  

---

### 🧠 Enriquecimento com LLM

```bash
python src/llm_enrich.py --date YYYY-MM-DD
```

- Calcula métricas antes de enviar ao LLM:  
  - `pct_change` em relação ao mês anterior  
  - `volatilidade` (desvio padrão dos retornos diários últimos N dias)  
  - `top movers` (5 moedas com maior variação absoluta)  
- Gera resumo compacto e envia ao LLM com prompt:  

```text
"Você é um analista financeiro. Receba estes dados agregados em JSON: {resumo} 
e gere um resumo executivo curto (3 frases), 3 insights acionáveis e alerta se 
volatilidade > limiar. Compare com mês anterior e cite percentuais."
```

- Log do **prompt** e da **resposta** em `/logs/llm/` com `timestamp`, `run_id` e hash.  

---

## 📂 Estrutura dos arquivos Parquet

- `date`: date  
- `base_currency`: string  
- `target_currency`: string  
- `rate`: float64  
- `rate_rounded`: float64 (opcional)  
- `retrieved_at`: timestamp  
- `run_id`: string  
- `pipeline_version`: string  

---

## 📊 Logging e Observabilidade

- Todos os logs em **JSON**, com campos padrão:  
  - `timestamp`, `service`, `level`, `message`, `run_id`, `filename`  
- **INFO** → eventos normais  
- **ERROR** → exceções  
- Métricas coletadas: número de cotações processadas, erros, tempo de execução.  
- `run_id` garante rastreabilidade entre **ingest → transform → load → llm**.  

---

## 🧪 Testes

- Testes unitários e de integração em `/tests/`.  
- Cobertura mínima:  
  - **Ingest:** trata erros HTTP e salva arquivo.  
  - **Transform:** remove taxas inválidas e produz colunas corretas.  
  - **Load:** grava Parquet com schema correto.  
  - **pct_change:** assert com números simples.  

---

## 📊 Dashboard Streamlit

* Executa offline usando os arquivos existentes em `data/gold/`.
* Lê **todos os Parquet** para mostrar evolução histórica.
* Lê **todos os insights JSON** e os exibe juntos.
* Filtros interativos permitem escolher moedas específicas.

```bash
streamlit run app.py
```

* Acesso pelo browser:  https://exchange-rate-pipelne-llm-kgexm2u6o4j5eyxohcoenz.streamlit.app/


---



