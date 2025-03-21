import pytest
import openai
from quotes.generator import generate_celebrity_quote

def test_generate_celebrity_quote_valid():
    """Test that a celebrity quote is generated correctly."""
    quote = generate_celebrity_quote("Albert Einstein")
    assert isinstance(quote, str), "Output should be a string"
    assert len(quote) > 0, "Generated quote should not be empty"


def test_generate_celebrity_quote_invalid_empty():
    """Test that an empty string returns an error message."""
    quote = generate_celebrity_quote("")
    assert quote == "Error: Celebrity name must be a valid string."

def test_generate_celebrity_quote_invalid_single_letter():
    """Test that a single letter returns an error."""
    quote = generate_celebrity_quote("A")
    print(f"DEBUG: Actual Output: {quote}")  # Debugging line
    assert quote == "Error: Invalid celebrity name. Please enter a first and last name."

def test_generate_celebrity_quote_invalid_symbols():
    """Test that names with symbols return an error."""
    quote = generate_celebrity_quote("@#$%")
    assert quote == "Error: Invalid celebrity name. Please enter a first and last name."

def test_generate_celebrity_quote_invalid_numbers():
    """Test that numbers return an error."""
    quote = generate_celebrity_quote("12345")
    assert quote == "Error: Invalid celebrity name. Please enter a first and last name."

def test_generate_celebrity_quote_invalid_mixed():
    """Test that mixed symbols and numbers return an error."""
    quote = generate_celebrity_quote("Einstein123!")
    assert quote == "Error: Invalid celebrity name. Please enter a first and last name."

