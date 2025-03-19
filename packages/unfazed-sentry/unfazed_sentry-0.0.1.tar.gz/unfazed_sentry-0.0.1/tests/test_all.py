from unittest.mock import patch

from unfazed.core import Unfazed
from unfazed.test import Requestfactory


async def test_sentry_capture_exception(unfazed: Unfazed) -> None:
    async with Requestfactory(unfazed) as client:
        with patch("sentry_sdk.capture_exception") as mock_capture_exception:
            await client.get("/")
            assert mock_capture_exception.call_count == 1


async def test_sentry_not_capture_exception(unfazed: Unfazed) -> None:
    async with Requestfactory(unfazed) as client:
        with patch("sentry_sdk.capture_exception") as mock_capture_exception:
            await client.get("/not-capture")
            assert mock_capture_exception.call_count == 0


async def test_sentry_with_scope(unfazed: Unfazed) -> None:
    async with Requestfactory(unfazed) as client:
        with patch("sentry_sdk.capture_exception") as mock_capture_exception:
            await client.get("/with-scope")
            assert mock_capture_exception.call_count == 1
