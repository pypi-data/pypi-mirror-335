import re
import random
import openai
from .chatgpt import chatgpt_generate
from .fallback import quotes, language_quotes

# Set to store used quotes during runtime (resets when the program restarts)
my_quotes = set()


def generate_quote():
    """Tries ChatGPT first. If it fails, falls back to predefined quotes."""
    global my_quotes

    try:
        quote = chatgpt_generate("Generate a unique inspirational quote.")
        if quote:  # make sure the response is not empty
            my_quotes.add(quote)
            return quote
    except openai.OpenAIError:
        pass

    available_quotes = [q for q in quotes if q not in my_quotes]

    if not available_quotes:
        return "No new fallback quotes left! Try again later."

    quote = random.choice(available_quotes)
    my_quotes.add(quote)
    return quote


def generate_celebrity_quote(celebrity):
    """Generates a quote attributed to a specific celebrity, with input validation."""
    global my_quotes

    # Ensure input is a valid full name
    if not isinstance(celebrity, str) or not celebrity.strip():
        return "Error: Celebrity name must be a valid string."

    # Reject invalid names (single words, numbers, special chars)
    if not re.fullmatch(r"[A-Za-z]+(?:\s[A-Za-z]+)+", celebrity):
        return "Error: Invalid celebrity name. Please enter a first and last name."

    prompt = f"Generate a famous quote that sounds like it was said by {celebrity}."

    try:
        quote = chatgpt_generate(prompt)
        if quote:
            quote = re.sub(
                rf"\b{celebrity}\b[.:!?]?\s*$", "", quote, flags=re.IGNORECASE
            ).strip()
            my_quotes.add(quote)
            return quote
    except openai.OpenAIError:
        pass

    # Fallback dictionary
    celebrity_quotes = {
        "Albert Einstein": [
            "Imagination is more important than knowledge.",
            "Life is like riding a bicycle. To keep your balance, you must keep moving.",
        ],
        "Oprah Winfrey": [
            "Turn your wounds into wisdom.",
            "The more you praise and celebrate your life, the more there is in life to celebrate.",
        ],
    }

    # Return fallback quote if available
    if celebrity in celebrity_quotes:
        available_quotes = [
            q for q in celebrity_quotes[celebrity] if q not in my_quotes
        ]
        if available_quotes:
            quote = random.choice(available_quotes)
            my_quotes.add(quote)
            return quote

    return f"Sorry, no quotes available for {celebrity}."


def generate_mood_quote(mood):
    global my_quotes

    if not isinstance(mood, str) or not mood.isalpha():
        return "Error: Mood must be a valid string."

    prompt = f"Generate a unique inspirational quote that matches the mood: {mood}."

    try:
        quote = chatgpt_generate(prompt)
        if quote:
            my_quotes.add(quote)
            return quote
    except openai.OpenAIError:
        pass

    mood_quotes = quotes.get(mood.lower(), [])

    available_quotes = [q for q in mood_quotes if q not in my_quotes]

    if not available_quotes:
        return f"No new fallback quotes left! Try again later."

    quote = random.choice(available_quotes)
    my_quotes.add(quote)
    return quote

def generate_language_quote(language):
    """Generates a quote in another language."""
    global my_quotes

    if not isinstance(language, str) or not language.isalpha():
        return "Error: Language must be a valid string."

    prompt = f"Generate a unique inspirational quote in {language}."

    try:
        quote = chatgpt_generate(prompt)
        if quote:
            my_quotes.add(quote)
            return quote
    except openai.OpenAIError:
        pass

    language_quote = language_quotes.get(language.lower(), [])

    available_quotes = [q for q in language_quote if q not in my_quotes]

    if not available_quotes:
        return f"No new fallback quotes left! Try again later."

    quote = random.choice(available_quotes)
    my_quotes.add(quote)
    return quote
