"""Tests for fact sanitizer"""

import pytest
from src.sanitizer import FactSanitizer, quick_sanitize


def test_sanitize_entities():
    """Test entity name sanitization"""
    sanitizer = FactSanitizer()

    text = "Cargill Meat Solutions LLC entered into an agreement with ABC Trading Corp."
    result = sanitizer.sanitize_text(text)

    assert "[Cargill Entity" in result
    assert "Cargill Meat Solutions LLC" not in result
    assert "[Third Party Entity" in result
    assert "ABC Trading Corp" not in result


def test_sanitize_people():
    """Test person name sanitization"""
    sanitizer = FactSanitizer()

    text = "John Smith, CFO, signed by Jane Doe (Manager)"
    result = sanitizer.sanitize_text(text)

    assert "[CFO]" in result
    assert "John Smith" not in result
    assert "[Manager]" in result
    assert "Jane Doe" not in result


def test_sanitize_amounts():
    """Test dollar amount sanitization"""
    sanitizer = FactSanitizer()

    text = "The payment was $1,234,567.89 USD and $500,000 respectively."
    result = sanitizer.sanitize_text(text)

    assert "$1,234,567.89" not in result
    assert "$500,000" not in result
    assert "[Amount]" in result


def test_sanitize_emails():
    """Test email sanitization"""
    sanitizer = FactSanitizer()

    text = "Contact john.smith@cargill.com or jane.doe@example.com"
    result = sanitizer.sanitize_text(text)

    assert "@cargill.com" not in result
    assert "@example.com" not in result
    assert "[Email]" in result


def test_redaction_report():
    """Test redaction report generation"""
    sanitizer = FactSanitizer()

    text = """
    Cargill Entity Inc. paid $100,000 to John Smith, CFO.
    Contact: john.smith@cargill.com
    """

    result = sanitizer.sanitize_text(text)
    report = sanitizer.get_report()

    assert report.entities_redacted > 0
    assert report.people_redacted > 0
    assert report.amounts_redacted > 0
    assert report.emails_redacted > 0
    assert report.total_redactions > 0


def test_quick_sanitize():
    """Test quick sanitize helper"""
    text = "Cargill Trading LLC paid $50,000"
    sanitized, report = quick_sanitize(text)

    assert "Cargill Trading LLC" not in sanitized
    assert "$50,000" not in sanitized
    assert report.total_redactions > 0


def test_entity_mapping_consistency():
    """Test that same entity gets same placeholder"""
    sanitizer = FactSanitizer()

    text = "Cargill A LLC and Cargill B LLC. Later, Cargill A LLC again."
    result = sanitizer.sanitize_text(text)

    # First occurrence of Cargill A LLC
    first_placeholder = None
    for entity, placeholder in sanitizer.entity_map.items():
        if "Cargill A LLC" in entity:
            first_placeholder = placeholder
            break

    assert first_placeholder is not None
    assert result.count(first_placeholder) == 2  # Should appear twice
