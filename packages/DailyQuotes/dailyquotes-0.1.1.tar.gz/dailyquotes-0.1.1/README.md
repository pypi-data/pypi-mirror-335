[![CI](https://github.com/software-students-spring2025/3-python-package-package_proj/actions/workflows/build.yaml/badge.svg?branch=run-workflow-on-main)](https://github.com/software-students-spring2025/3-python-package-package_proj/actions/workflows/build.yaml)

An exercise to create a Python package, build it, test it, distribute it, and use it. See [instructions](./instructions.md) for details.

# dailyquotes

## Contributors:

[Aaqila Patel](https://github.com/aaqilap)

[Andy Cabindol](https://github.com/andycabindol)

[Lina Sanchez](https://github.com/linahsan)

[Maya Mabry](https://github.com/mam10023)

## Description:

dailyquotes is a simple Python package that generates random quotes including quotes that are well-known, from celebrities, mood based, and in different languages. This python package provides an easy way to integrate meaningful quotes into projects, daily routines, or personal motivation.

## Installation 

You can install dailyquotes directly from [PyPI](https://pypi.org/project/DailyQuotes/)
```bash
pip install dailyquotes
```

## Features 
dailyquotes offers four different features within the package:

### 1. generate_quote
This function generates a random quote and is perfect for a user who wants an entertaining quote without any specific criteria. 

```bash
from dailyquotes import generate_quote
quote = generate_quote()
print(quote)
# Output: "The only way to do great work is to love what you do."
```


### 2. generate_celebrity_quote 
This function allows users to specify a celebrity (ex. musician, politician, historical figure, etc.) and receive a quote attributed to them. 

```bash
from dailyquotes import generate_celebrity_quote
quote = generate_celebrity_quote("Albert Einstein")
print(quote)
# Output: "Imagination is the light that illuminates the realms of knowledge and discovery."
```

### 3. generate_mood_quote 
This function allows users to input their mood (ex. happy, sad, excitement), and the function will return a quote that aligns with their emotional state. 

```bash
from dailyquotes import generate_mood_quote
quote = generate_mood_quote("sad")
print(quote)
# Output: "Even when sorrow clouds the skies, remember that every raindrop has the potential to nurture a seed into a beautiful flower."
```

### 4. generate_language_quote
This function generates a quote in a user-specified language (Spanish, French, Greek) which is useful for language learners.

```bash
from dailyquotes import generate_language_quote
quote = generate_language_quote("Greek")
print(quote)
# Output: "Η επιμονή είναι η αδερφή της επιτυχίας"
```

## Command Line Usage 
dailyquotes can also be used directly from the command line: 

```bash
# Install the package 
pip install dailyquotes

# Run the CLI
python -m dailyquotes
```

## Example Program 
Here is a complete example program that demonstrates all functions:

[example.py](https://github.com/software-students-spring2025/3-python-package-package_proj/blob/main/example.py)


## Development Setup
If you would like to contribute to dailyquotes, follow these steps: 

### Prerequisites 
- Python 3.7 or higher 
- pipenv

### Environmental Variables 
This package requires an OpenAI API Key to generate quotes dynamically.
- You need to create a ```.env``` file and add the API key
- Contact [Andy Cabindol](https://github.com/andycabindol) to obtain the ```.env``` file with the required API key. 

### Setup steps 
1. Clone the repository: 

```bash
git clone https://github.com/software-students-spring2025/3-python-package-package_proj.git

cd 3-python-package-package_proj

```

2. Set up the virtual environment and install dependencies: 

```bash
pipenv install --dev 
pipenv shell

```

3. Install the package in development mode: 

```bash
pipenv install -e .
```


### Running tests
We use pytest for testing. To run the tests: 

```bash
pytest
```

### Building the package 
To build the package: 

```bash
python -m build
```
This will generate distribution files in the dist/ directory.

### Workflow for contributions 
1. Create a new branch for your feature: 

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and write tests if necessary 

3. Run tests to ensure everything works: 
```bash
pytest
```

4. Commit your changes and push to your branch
```bash
git add . 
git commit -m "Add feature: unique feature description"
git push origin feature/your-feature-name

```

5. Create a Pull Request to the 'main' branch
