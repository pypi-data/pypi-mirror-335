import pytest
import openai
from quotes.generator import generate_language_quote


def test_generate_language_quote_valid():
    """Test that a language quote is generated correctly."""
    quote = generate_language_quote("french")
    assert isinstance(quote, str), "Output should be a string"
    assert len(quote) > 0, "Generated quote should not be empty"


def test_generate_celebrity_quote_invalid_empty():
    """Test that an empty string returns an error message."""
    quote = generate_language_quote("")
    assert quote == "Error: Language must be a valid string."


def test_generate_celebrity_quote_invalid_symbols():
    """Test that string with symbols return an error."""
    quote = generate_language_quote("@#$%")
    assert quote == "Error: Language must be a valid string."


def test_generate_celebrity_quote_invalid_numbers():
    """Test that numbers return an error."""
    quote = generate_language_quote("12345")
    assert quote == "Error: Language must be a valid string."


def test_generate_celebrity_quote_invalid_mixed():
    """Test that mixed symbols and numbers return an error."""
    quote = generate_language_quote("english123!")
    assert quote == "Error: Language must be a valid string."
