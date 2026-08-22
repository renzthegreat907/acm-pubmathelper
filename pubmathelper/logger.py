import logging
import os

import psutil

logger = logging.getLogger(__name__)
process = psutil.Process(os.getpid())

_previous_rss = None


def log_memory(label: str) -> None:
    global _previous_rss

    rss = process.memory_info().rss
    rss_mb = rss / (1024 ** 2)

    if _previous_rss is None:
        logger.info(
            "[MEMORY] %s | RSS: %.2f MB",
            label,
            rss_mb,
        )
    else:
        delta_mb = (rss - _previous_rss) / (1024 ** 2)

        logger.info(
            "[MEMORY] %s | RSS: %.2f MB | Δ: %+.2f MB",
            label,
            rss_mb,
            delta_mb,
        )

    _previous_rss = rss