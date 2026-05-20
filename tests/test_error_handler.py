# Copyright 2024 Owen
#
# Licensed under the MIT License

"""Tests for src/utils/error_handler.py."""

import os
import pytest
from src.utils.error_handler import (
    ErrorMessages,
    check_api_keys,
    check_model_api_key,
    README_URL,
)


class TestErrorMessages:
    """Tests for ErrorMessages class."""

    def test_all_error_messages_are_non_empty_strings(self):
        """Every ErrorMessages attribute is a non-empty string."""
        for name in dir(ErrorMessages):
            if name.startswith('_'):
                continue
            attr = getattr(ErrorMessages, name)
            assert isinstance(attr, str), f"{name} is not a string"
            assert len(attr) > 0, f"{name} is empty"

    def test_readme_url_is_valid(self):
        """README_URL points to the project repository."""
        assert README_URL.startswith("https://github.com/")
        assert "CyberScraper-2077" in README_URL


class TestCheckApiKeys:
    """Tests for check_api_keys()."""

    def test_returns_list(self):
        """check_api_keys returns a list."""
        result = check_api_keys()
        assert isinstance(result, list)

    def test_no_errors_when_keys_present(self, monkeypatch):
        """No errors returned when both keys are set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        result = check_api_keys()
        assert result == []

    def test_openai_missing_returns_error(self, monkeypatch):
        """OPENAI_API_KEY missing returns error message."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        result = check_api_keys()
        assert any("OpenAI" in msg for msg in result)

    def test_google_missing_returns_error(self, monkeypatch):
        """GOOGLE_API_KEY missing returns error message."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = check_api_keys()
        assert any("Google" in msg for msg in result)


class TestCheckModelApiKey:
    """Tests for check_model_api_key()."""

    def test_returns_none_for_known_gpt_model_when_key_present(self, monkeypatch):
        """Returns None for gpt-4 when OPENAI_API_KEY is set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        result = check_model_api_key("gpt-4")
        assert result is None

    def test_returns_none_for_known_gemini_model_when_key_present(self, monkeypatch):
        """Returns None for gemini-1.5-flash when GOOGLE_API_KEY is set."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test")
        result = check_model_api_key("gemini-1.5-flash")
        assert result is None

    def test_returns_error_for_gpt_model_without_key(self, monkeypatch):
        """Returns error message for gpt-4 without OPENAI_API_KEY."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = check_model_api_key("gpt-4")
        assert result is not None
        assert "OpenAI" in result

    def test_returns_error_for_gemini_model_without_key(self, monkeypatch):
        """Returns error message for gemini-1.5-flash without GOOGLE_API_KEY."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = check_model_api_key("gemini-1.5-flash")
        assert result is not None
        assert "Google" in result

    def test_returns_none_for_unknown_model(self, monkeypatch):
        """Returns None for model without specific key requirement."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = check_model_api_key("unknown-model")
        assert result is None


class TestErrorMessageContent:
    """Tests for specific error message content."""

    def test_tor_error_contains_install_instructions(self):
        """TOR_PROXY_CONNECTION_FAILED contains installation instructions."""
        msg = ErrorMessages.TOR_PROXY_CONNECTION_FAILED
        assert "apt" in msg or "brew" in msg

    def test_api_key_error_contains_env_var_name(self):
        """API key error messages mention the environment variable name."""
        assert "OPENAI_API_KEY" in ErrorMessages.OPENAI_API_KEY_MISSING
        assert "GOOGLE_API_KEY" in ErrorMessages.GOOGLE_API_KEY_MISSING

    def test_url_invalid_contains_onion_hint(self):
        """ONION_URL_INVALID mentions .onion requirement."""
        assert ".onion" in ErrorMessages.ONION_URL_INVALID


if __name__ == "__main__":
    pytest.main([__file__, "-v"])