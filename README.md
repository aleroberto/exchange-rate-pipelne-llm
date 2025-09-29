# exchange-rate-pipelne-llm
Pipeline de cotações cambiais com Python, armazenamento em camadas (raw, silver, gold) e geração de insights com LLM.

## Estrutura inicial de diretórios

- /data/raw         → Dados brutos coletados da API de câmbio
- /data/silver      → Dados transformados e validados em formato parquet
- /data/gold        → Dados finais prontos para consumo analítico e relatórios

## Configuração de variáveis de ambiente

Para rodar este projeto, criar um arquivo `.env` com as variáveis:
EXCHANGE_API_KEY= (Preencher com a respectiva chave de API)
EXCHANGE_BASE_URL=(Preencher a URI corresondente)
OPENAI_API_KEY=(Preencher com a respectiva chave de API)
DB_URI=(Preencher a URI corresondente ao Banco)
ENV=dev (Preencher com DEV ou PROD)


## Testes e Qualidade

Para garantir que o pipeline funciona corretamente, criamos testes unitários e de integração usando pytest.  

### Estrutura de testes
- `tests/` → todos os testes unitários e de integração.
- `tests/fixtures/` → arquivos de exemplo usados nos testes.
- Testes cobrem:
  - Ingestão: trata erros HTTP e salva arquivo corretamente.
  - Transformação: remove taxas nulas/negativas, produz colunas esperadas e remove duplicatas.
  - Carga: grava arquivos Parquet com esquema correto.
  - Cálculo de métricas do LLM: pct_change, volatilidade, top movers.

### Rodando os testes

1. Instale as dependências do projeto:
pip install -r requirements.txt

2. Execute o pytest a partir da raiz do projeto:
python -m pytest

- Todos os testes devem passar.  
