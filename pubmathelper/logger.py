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
        print(
            f"[MEMORY] {label} | RSS: {rss_mb:.2f} MB",
            flush=True,
        )
    else:
        delta_mb = (rss - _previous_rss) / (1024 ** 2)

        print(
            f"[MEMORY] {label} | RSS: {rss_mb:.2f} MB | Δ: {delta_mb:+.2f} MB",
            flush=True
        )

    _previous_rss = rss

def log_misc(message: str) -> None:
    print(
        f"[MISC] {message}",
        flush=True
    )