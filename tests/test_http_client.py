# Copyright 2024 Owen
#
# Licensed under the MIT License

"""Tests for src/http_client.py."""

import pytest
import aiohttp

from src.http_client import (
    get_session,
    close_session,
    http_session,
    fetch_url,
    fetch_json,
    DEFAULT_TIMEOUT,
    DEFAULT_HEADERS,
)


class TestGetSession:
    """Tests for get_session()."""

    @pytest.mark.asyncio
    async def test_returns_client_session(self):
        """get_session() returns a ClientSession instance."""
        session = await get_session()
        assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_returns_same_session(self):
        """Multiple calls return the same singleton session."""
        session1 = await get_session()
        session2 = await get_session()
        assert session1 is session2

    @pytest.mark.asyncio
    async def test_recreates_closed_session(self):
        """A closed session is recreated on next call."""
        session1 = await get_session()
        await close_session()
        session2 = await get_session()
        # After close, we get a new session (not the old closed one)
        assert not session2.closed


class TestHttpSession:
    """Tests for http_session() context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_yields_session(self):
        """http_session() yields a valid ClientSession."""
        async with http_session() as session:
            assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_context_manager_reuses_session(self):
        """Session is reused across context manager calls."""
        async with http_session() as session1:
            pass
        async with http_session() as session2:
            assert session1 is session2


class TestDefaultConfig:
    """Tests for default configuration values."""

    def test_default_timeout_total(self):
        """DEFAULT_TIMEOUT has total set to 60."""
        assert DEFAULT_TIMEOUT.total == 60

    def test_default_timeout_connect(self):
        """DEFAULT_TIMEOUT has connect set to 10."""
        assert DEFAULT_TIMEOUT.connect == 10

    def test_default_headers_contains_user_agent(self):
        """DEFAULT_HEADERS includes a User-Agent."""
        assert 'User-Agent' in DEFAULT_HEADERS
        assert 'Mozilla/5.0' in DEFAULT_HEADERS['User-Agent']

    def test_default_headers_accept_language(self):
        """DEFAULT_HEADERS includes Accept-Language."""
        assert 'Accept-Language' in DEFAULT_HEADERS


class TestFetchUrl:
    """Tests for fetch_url()."""

    @pytest.mark.asyncio
    async def test_fetch_url_404(self):
        """fetch_url raises ClientResponseError for 404."""
        with pytest.raises(aiohttp.ClientResponseError):
            await fetch_url("https://httpbin.org/status/404")

    @pytest.mark.asyncio
    async def test_fetch_url_invalid_host(self):
        """fetch_url raises ClientError for invalid host."""
        with pytest.raises(aiohttp.ClientError):
            await fetch_url("https://this-domain-does-not-exist-xyz.invalid/")


class TestFetchJson:
    """Tests for fetch_json()."""

    @pytest.mark.asyncio
    async def test_fetch_json_invalid(self):
        """fetch_json raises error for non-JSON response."""
        with pytest.raises(aiohttp.ClientError):
            await fetch_json("https://httpbin.org/html")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
