from typing import Any

import pytest

from matomo_core.trackers import PerfMsTracker
from tests import shared  # type: ignore


def test_perf_ms_tracker_sync(snapshot_json) -> None:  # noqa: ANN001
    scope: dict[str, Any] = {"tracking_data": {}}
    with PerfMsTracker(scope=scope, key="pf_srv"):
        _a = 2**0.3
    assert scope["tracking_data"] == snapshot_json(matcher=shared.make_matcher(pf_srv=(float,)))


@pytest.mark.asyncio
async def test_perf_ms_tracker_async(snapshot_json) -> None:  # noqa: ANN001
    scope: dict[str, Any] = {"tracking_data": {}}
    async with PerfMsTracker(scope=scope, key="pf_srv"):
        _a = 2**0.3
    assert scope["tracking_data"] == snapshot_json(matcher=shared.make_matcher(pf_srv=(float,)))
