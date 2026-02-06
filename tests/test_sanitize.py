"""Tests for HTML sanitization."""

import pytest
from excel_radar.sanitizer import (
    clean_text,
    is_html_escaped,
    sanitize_html,
    add_link_security,
    sanitize_description,
)


class TestCleanText:
    """Test text cleaning functions."""

    def test_trim_whitespace(self):
        assert clean_text("  hello  ") == "hello"
        assert clean_text("\n\thello\n\t") == "hello"

    def test_smart_quotes(self):
        assert clean_text(""hello"") == '"hello"'
        assert clean_text("'hello'") == "'hello'"

    def test_collapse_spaces(self):
        assert clean_text("hello    world") == "hello world"
        assert clean_text("hello\n\n\nworld") == "hello world"

    def test_empty_string(self):
        assert clean_text("") == ""
        assert clean_text("   ") == ""


class TestHtmlEscaping:
    """Test HTML escaping detection."""

    def test_detect_escaped_html(self):
        assert is_html_escaped("<p>Hello</p>")
        assert is_html_escaped("Hello & World")
        assert is_html_escaped("&#60;div&#62;")

    def test_detect_unescaped_html(self):
        assert not is_html_escaped("<p>Hello</p>")
        assert not is_html_escaped("Hello World")


class TestSanitizeHtml:
    """Test HTML sanitization."""

    def test_allow_safe_tags(self):
        html = "<p>Hello <strong>world</strong></p>"
        result = sanitize_html(html)
        assert "<p>" in result
        assert "<strong>" in result

    def test_remove_dangerous_tags(self):
        html = "<script>alert('xss')</script><p>Hello</p>"
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "<p>Hello</p>" in result

    def test_unescape_html_entities(self):
        html = "<p>Hello</p>"
        result = sanitize_html(html)
        assert "<p>Hello</p>" in result

    def test_preserve_links(self):
        html = '<p>Visit <a href="https://example.com">our site</a></p>'
        result = sanitize_html(html)
        assert 'href="https://example.com"' in result
        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_empty_input(self):
        assert sanitize_html("") == ""
        assert sanitize_html(None) == ""


class TestAddLinkSecurity:
    """Test link security attributes."""

    def test_add_target_blank(self):
        html = '<a href="https://example.com">Link</a>'
        result = add_link_security(html)
        assert 'target="_blank"' in result

    def test_add_rel_noopener(self):
        html = '<a href="https://example.com">Link</a>'
        result = add_link_security(html)
        assert 'rel="noopener noreferrer"' in result

    def test_preserve_existing_attributes(self):
        html = '<a href="https://example.com" title="Test">Link</a>'
        result = add_link_security(html)
        assert 'title="Test"' in result
        assert 'target="_blank"' in result


class TestSanitizeDescription:
    """Test description sanitization."""

    def test_sanitize_valid_html(self):
        desc = "<p>This is a <strong>test</strong> description.</p>"
        result = sanitize_description(desc)
        assert "<p>" in result
        assert "<strong>" in result

    def test_sanitize_escaped_html(self):
        desc = "<p>Test</p>"
        result = sanitize_description(desc)
        assert "<p>Test</p>" in result

    def test_handle_none(self):
        assert sanitize_description(None) == ""

    def test_handle_empty_string(self):
        assert sanitize_description("") == ""

    def test_remove_script_tags(self):
        desc = "<p>Hello</p><script>alert('xss')</script>"
        result = sanitize_description(desc)
        assert "<script>" not in result
        assert "<p>Hello</p>" in result

# Made with Bob
