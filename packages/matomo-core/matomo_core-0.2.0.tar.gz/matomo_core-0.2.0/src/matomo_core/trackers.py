"""Trackers to measure time."""

import time
import typing


class PerfMsTracker:
    """Measure time between enter and exit and records it in state.

    >>> scope = {"tracking_data": {}}
    >>> with PerfMsTracker(scope, key="pf_srv"):
    ...     _a = 2 + 2 # do computation
    >>> assert "pf_srv" in scope["tracking_data"]
    """

    def __init__(self, scope: typing.MutableMapping[str, typing.Any], key: str) -> None:
        """Initialize the PerfMsTracker.

        Args:
            scope: mapping of tracked data
            key: the key to use to store this measurement.
        """
        self.start_ns = 0.0
        self.scope = scope
        self.key = key

    def __enter__(self) -> None:  # noqa: D105
        self.start_ns = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:  # noqa: ANN001, D105
        self._record_time(self.key, time.perf_counter_ns())

    async def __aenter__(self) -> None:  # noqa: D105
        self.start_ns = time.perf_counter_ns()

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:  # noqa: ANN001, D105
        self._record_time(self.key, time.perf_counter_ns())

    def _record_time(self, key: str, end_ns: float) -> None:
        elapsed_time_ms = (end_ns - self.start_ns) / 1000.0
        self.scope["tracking_data"][key] = elapsed_time_ms
