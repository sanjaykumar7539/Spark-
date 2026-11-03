"""Run the configured batch medallion pipeline."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone

from audit import write_quality_report, write_run_audit
from bronze import run as run_bronze
from config import configured_path, load_config
from gold import run as run_gold
from silver import run as run_silver
from spark_session import create_spark_session


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> int:
    config = load_config()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    counts: dict[str, int] = {}
    spark = create_spark_session(config["project"]["name"])
    try:
        bronze = run_bronze(spark, config)
        counts["bronze_rows"] = bronze.count()
        LOGGER.info("Bronze completed: %d rows", counts["bronze_rows"])
        silver = run_silver(spark, config)
        counts["silver_rows"] = silver.count()
        LOGGER.info("Silver completed: %d rows", counts["silver_rows"])
        gold = run_gold(spark, config)
        counts["gold_rows"] = gold.count()
        LOGGER.info("Gold completed: %d rows", counts["gold_rows"])
        counts["quarantined_rows"] = (
            spark.read.parquet(str(configured_path("silver", "quarantine"))).count()
            if configured_path("silver", "quarantine").exists()
            else 0
        )
        write_quality_report(
            config,
            run_id,
            {
                "bronze_to_silver_retention": counts["silver_rows"] / max(counts["bronze_rows"], 1),
                "quarantined_rows": counts["quarantined_rows"],
                "gold_has_rows": counts["gold_rows"] > 0,
            },
        )
        write_run_audit(config, run_id, "success", counts)
        return 0
    except Exception as exc:
        write_run_audit(config, run_id, "failed", counts, str(exc))
        LOGGER.exception("Pipeline failed")
        return 1
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
