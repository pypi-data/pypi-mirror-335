import pytest
from quotes.generator import generate_quote

def test_generate_quote_is_string():
    """Test that generate_quote returns a string."""
    quote = generate_quote()
    assert isinstance(quote, str), "Generated quote should be a string"

def test_generate_quote_is_valid():
    """Test that generate_quote returns a non-empty quote."""
    quote = generate_quote()
    assert len(quote) > 0, "Generated quote should not be empty"

def test_generate_quote_is_unique():
    """Test that generate_quote generates unique quotes."""
    quote1 = generate_quote()
    quote2 = generate_quote()
    assert quote1 != quote2, "Generated quotes should be unique"
