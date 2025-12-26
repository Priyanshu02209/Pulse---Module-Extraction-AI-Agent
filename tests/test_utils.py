"""Unit tests for utils module."""
from src.utils import (
    dedupe_preserve_order,
    is_same_domain,
    looks_like_binary,
    normalize_url,
)


class TestNormalizeUrl:
    def test_handles_absolute_urls(self):
        assert normalize_url("https://example.com", "https://example.com/page") == "https://example.com/page"

    def test_handles_relative_urls(self):
        assert normalize_url("https://example.com/base", "/page") == "https://example.com/page"

    def test_removes_fragments(self):
        url = normalize_url("https://example.com", "https://example.com/page#section")
        assert url == "https://example.com/page"

    def test_rejects_non_http_schemes(self):
        assert normalize_url("https://example.com", "ftp://example.com/file") == ""


class TestIsSameDomain:
    def test_matches_same_domain(self):
        assert is_same_domain("https://example.com", "https://www.example.com")
        assert is_same_domain("https://example.com/page", "https://example.com/other")

    def test_rejects_different_domains(self):
        assert not is_same_domain("https://example.com", "https://other.com")


class TestLooksLikeBinary:
    def test_detects_binary_types(self):
        assert looks_like_binary("application/pdf")
        assert looks_like_binary("image/png")
        assert looks_like_binary("application/zip")

    def test_allows_text_types(self):
        assert not looks_like_binary("text/html")
        assert not looks_like_binary("application/json")


class TestDedupePreserveOrder:
    def test_removes_duplicates(self):
        items = ["a", "b", "a", "c", "b"]
        result = dedupe_preserve_order(items)
        assert result == ["a", "b", "c"]

    def test_preserves_order(self):
        items = ["z", "a", "b", "a"]
        result = dedupe_preserve_order(items)
        assert result == ["z", "a", "b"]

