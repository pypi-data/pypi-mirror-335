from setuptools import setup, find_packages

setup(
    name="hashai",
    version="0.3.17",
    description="A powerful SDK for building AI assistants with RAG capabilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rakesh",
    author_email="rakeshsahoo689@gmail.com",
    url="https://github.com/Syenah/opAI",
    packages=find_packages(),
    install_requires=[
        "openai",
        "anthropic",
        "groq",
        "google-genai",
        "mistralai",
        "faiss-cpu",  # For vector storage
        "pydantic",   # For data validation
        "requests",   # For web tools
        "playwright", # For web scraping
        "fastapi",    #	For creating the RESTful API
        "uvicorn",    # For running the FastAPI app
        "pillow",     # For image processing
        "slowapi",    # For rate limiting
        "sentence-transformers", # For sentence embeddings
        "fuzzywuzzy", # For fuzzy string matching
        "duckduckgo-search", # For DuckDuckGo search
        "yfinance",   # For stock/crypto prices
        "cryptography", # For encryption

    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hashai=hashai.cli.main:main",
        ],
    },
)