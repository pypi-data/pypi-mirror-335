from setuptools import setup, find_packages

setup(
    name="quotes_generator",  # Name of the package on PyPI
    version="0.1.1",  # Version number
    packages=find_packages(where="src"),  # Finds packages inside 'src' directory
    package_dir={"": "src"},  # Maps package root to 'src'
    install_requires=[],  # Add dependencies here if needed, e.g., ["requests"]
    entry_points={
        "console_scripts": [
            "random-quote=quotes.generator:get_random_quote",
        ],
    },
    author="Your Name",
    author_email="your_email@example.com",
    description="A fun Python package to generate and search for jokes and motivational quotes.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/quotes-generator",  # Update this with your repo
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Set minimum Python version
    include_package_data=True,  # Ensures non-Python files are included if specified in MANIFEST.in
)
