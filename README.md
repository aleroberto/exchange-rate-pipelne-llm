# exchange-rate-pipeline-llm

Pipeline de cotações cambiais com Python, armazenamento em camadas (raw, silver, gold) e geração de insights com LLM.

## Estrutura de diretórios

* `/data/raw/` → Dados brutos coletados da API, incluindo metadados (timestamp, status HTTP, URL).
* `/data/raw/rejects/` → Linhas rejeitadas durante a transformação, com motivo.
* `/data/silver/` → Dados transformados e validados em formato Parquet.
* `/data/gold/` → Dados finais prontos para consumo analítico e relatórios.
* `/data/gold/insights/` → Relatórios de insights gerados pelo LLM.
* `/logs/` → Logs estruturados em JSON de todas as etapas.
* `/src/` → Código do pipeline (`ingest.py`, `transform.py`, `load.py`, `llm_enrich.py`, `utils.py`).
* `/tests/` → Testes unitários e de integração.

## Pré-requisitos e instalação

1. Ter Python 3.x instalado.
2. Criar e ativar um ambiente virtual:

```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate    # Windows
```

3. Instalar dependências:

```
pip install -r requirements.txt
```

4. Criar arquivo `.env` na raiz do projeto com as variáveis:

```
EXCHANGE_API_KEY=<sua_chave>
EXCHANGE_BASE_URL=<URI_da_API>
OPENAI_API_KEY=<sua_chave>
DB_URI=<URI_do_banco>
ENV=dev  # ou PROD
```

## Executando o pipeline

### Ingestão

```
python src/ingest.py --date YYYY-MM-DD
```

* Salva JSON bruto em `/data/raw/YYYY-MM-DD.json`.
* Se houver mais de uma coleta no dia: `/data/raw/YYYY-MM-DD_HHMMSS.json`.
* Inclui metadados: timestamp, status HTTP, URL.
* Logs estruturados em JSON em `/logs/`.

### Transformação

```
python src/transform.py --date YYYY-MM-DD
```

* Lê JSON bruto correspondente à data.
* Normaliza em DataFrame com colunas obrigatórias:

  * `base_currency` (string)
  * `target_currency` (string)
  * `rate` (float, arredondado 6 casas)
  * `retrieved_at` (timestamp ISO)
  * `date` (YYYY-MM-DD)
* Valida taxas (não nulas, não zero, não negativas).
* Remove duplicatas (`target_currency` + `retrieved_at`).
* Linhas inválidas vão para `/data/raw/rejects/` com motivo.
* Resultado limpo gravado em `/data/silver/YYYY-MM-DD.parquet`.

### Carga final

```
python src/load.py --date YYYY-MM-DD
```

* Agrega arquivos `/data/silver/`.
* Gera artefato final `/data/gold/YYYY-MM-DD.parquet`.
* Inclui metadados: `run_id` (UUID), `pipeline_version`, timestamp.
* Garantia de índice único (`date + base_currency + target_currency`) para evitar duplicatas.
* Pode gravar em banco relacional via SQLAlchemy.

### Enriquecimento com LLM

```
python src/llm_enrich.py --date YYYY-MM-DD
```

* Calcula métricas antes de enviar ao LLM:

  * `pct_change` em relação ao mês anterior
  * `volatilidade` (desvio padrão retornos diários últimos N dias)
  * `top movers` (5 moedas com maior variação absoluta)
* Gera resumo compacto e envia ao LLM:

```
"Você é um analista financeiro. Receba estes dados agregados em JSON: {resumo} e gere um resumo executivo curto (3 frases), 3 insights acionáveis e alerta se volatilidade > limiar. Compare com mês anterior e cite percentuais."
```

* Log do prompt e resposta em `/logs/llm/` com `timestamp`, `run_id` e hash.

## Estrutura dos arquivos Parquet

* `date`: date
* `base_currency`: string
* `target_currency`: string
* `rate`: float64
* `rate_rounded`: float64 (opcional)
* `retrieved_at`: timestamp
* `run_id`: string
* `pipeline_version`: string

## Logging e observabilidade

* Todos os logs em JSON, campos padrão:

  * `timestamp`, `service`, `level`, `message`, `run_id`, `filename`
* INFO → eventos normais, ERROR → exceções
* Métricas: número de cotações processadas, erros, tempo de execução
* Run_id para rastreabilidade ingest → transform → load → llm

## Testes

* Testes unitários e de integração em `/tests/`
* Cobertura mínima:

  * Ingest: trata erros HTTP e salva arquivo
  * Transform: remove taxas inválidas, produz colunas corretas
  * Load: grava Parquet com schema correto
  * pct_change: assert com números simples
* Executar:

```
python -m pytest
```



