import os
import time
import pandas as pd
from datetime import datetime
from src import ingest, transform, load, llm_enrich
from src.logging_config import get_logger, get_run_id, log_metrics

# ---------------------------
# Inicialização do pipeline
# ---------------------------
run_id = get_run_id()
logger = get_logger(run_id=run_id, service="pipeline")
logger.info("pipeline_start", run_id=run_id)

def main():
    start_time = time.time()
    try:
        # ---------------------------
        # ETAPA 1: Ingestão
        # ---------------------------
        raw_file = ingest.fetch_exchange_rates(base_currency="USD")
        logger.info("ingest_complete", arquivo=raw_file, run_id=run_id)
        elapsed = time.time() - start_time
        log_metrics(logger, "ingest", 1, elapsed)  # 1 arquivo processado

        # ---------------------------
        # ETAPA 2: Transformação
        # ---------------------------
        silver_file = transform.transform_file(raw_file, run_id=run_id)
        elapsed = time.time() - start_time
        log_metrics(logger, "transform_total", 1, elapsed)

        # ---------------------------
        # ETAPA 3: Carga
        # ---------------------------
        gold_file = load.aggregate_silver_files(run_id=run_id)
        elapsed = time.time() - start_time
        log_metrics(logger, "load_total", 1, elapsed)

        # ---------------------------
        # ETAPA 4: Enriquecimento LLM
        # ---------------------------
        df = pd.read_parquet(silver_file)
        llm_summary = llm_enrich.enrich_with_llm(df, run_id=run_id, simulate_llm=True)
        logger.info("llm_enrichment_complete", run_id=run_id, summary=llm_summary)

    except Exception as e:
        logger.error("pipeline_failed", run_id=run_id, error=str(e))
        raise

    finally:
        elapsed = time.time() - start_time
        logger.info(
            "pipeline_end",
            run_id=run_id,
            elapsed_seconds=round(elapsed, 2)
        )

if __name__ == "__main__":
    main()
