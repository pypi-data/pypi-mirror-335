import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()


# Set OpenAI API key globally
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OpenAI API key not found. Set it in the .env file.")

def chatgpt_generate(prompt):
    """Generates a quote using OpenAI's new API format."""
    client = openai.OpenAI()  # Required for OpenAI >= 1.0.0
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

