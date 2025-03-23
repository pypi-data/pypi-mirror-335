# HashAI: The Mother of Your AI Agents

HashAI is an advanced SDK designed to simplify the creation of AI agents. Whether you’re building a research assistant, a customer support bot, or a personal AI, HashAI provides all the tools and integrations to make it easy.

We currently support **Groq**, **OpenAI**, and **Anthropic** LLMs, along with a Retrieval-Augmented Generation (RAG) system for enhanced context-awareness.

## Installation
Install HashAI via pip:
```bash
pip install hashai
```

## Features
- **Seamless LLM Integration**: Plug-and-play support for Groq, OpenAI, and Anthropic.
- **RAG Support**: Retrieval-Augmented Generation for contextually aware responses.
- **Customizable Agents**: Define the personality, behavior, and instructions for your AI agents.
- **Extensibility**: Add new tools or modify behavior with ease.

## Example: Blockchain Research Assistant
This example demonstrates how to create a blockchain research assistant using HashAI and the Groq LLM.

### Prerequisites
1. Set up your Groq API key as an environment variable or directly in the code.

```python
import os
os.environ["GROQ_API_KEY"] = "your-api-key"  # Replace with your Groq API key
```

2. Import the HashAI Assistant class and configure your agent.

### Code Example
```python
# Set the Groq API key (either via environment variable or explicitly)
import os
os.environ["GROQ_API_KEY"] = "your-api-key"  # Set the API key here

# Initialize the Assistant
from hashai.assistant import Assistant

healthcare_research_assistant = Assistant(
    name="Healthcare Assistant",
    description="Extract and structure medical information from the provided text into a JSON format used in healthcare",
    instructions=[
        "Always use medical terminology while creating json",
        "Extract and structure medical information from the provided text into a JSON format used in healthcare",
    ],
    model="Groq",
    show_tool_calls=True,
    user_name="Researcher",
    emoji=":chains:",
    markdown=True,
)
patient_text = """
Patient Complaints of High grade fever, chest pain, radiating towards right shoulder. Sweating,
patient seams to have high grade fever ,  patient is allergic to pollution , diagnosis high grade fever , plan of care comeback after 2 days , instructions take rest and drink lot of water  Palpitation since 5 days.
Advice investigation: CBC, LFT, Chest X ray, Abdomen Ultrasound
Medication: Diclofenac 325mg twice a day for 5 days, Amoxiclave 625mg once a day for 5 days, Azithromycin 500mg Once a day
Ibuprofen SOS, Paracetamol sos, Pentoprazol before breakfast  , follow up after 2 days
"""
# Test the Assistant
healthcare_research_assistant.print_response(patient_text)
```

## File Structure
The HashAI SDK is organized as follows:
```
opData/
├── hashai/                      # Core package
│   ├── __init__.py              # Package initialization
│   ├── assistant.py             # Core Assistant class
│   ├── agent.py                 # Core Agent class
│   ├── rag.py                   # RAG functionality
│   ├── memory.py                # Conversation memory management
│   ├── llm/                     # LLM integrations
│   │   ├── __init__.py
│   │   ├── openai.py            # OpenAI integration
│   │   ├── anthropic.py         # Anthropic (Claude) integration
│   │   ├── llama.py             # Llama 2 integration
│   │   └── base_llm.py          # Base class for LLMs
│   ├── knowledge_base/          # Knowledge base integration
│   │   ├── __init__.py
│   │   ├── vector_store.py      # Vector store for embeddings
│   │   ├── document_loader.py   # Load documents into the knowledge base
│   │   └── retriever.py         # Retrieve relevant documents
│   ├── tools/                   # Tools for assistants
│   │   ├── __init__.py
│   │   ├── calculator.py        # Example tool: Calculator
│   │   ├── web_search.py        # Example tool: Web search
│   │   └── base_tool.py         # Base class for tools
│   ├── storage/                 # Storage for memory and data
│   │   ├── __init__.py
│   │   ├── local_storage.py     # Local file storage
│   │   └── cloud_storage.py     # Cloud storage (e.g., S3, GCP)
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging utility
│   │   └── config.py            # Configuration loader
│   └── cli/                     # Command-line interface
│       ├── __init__.py
│       └── main.py              # CLI entry point
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_assistant.py
│   ├── test_rag.py
│   └── test_memory.py
├── examples/                    # Example usage
│   ├── basic_assistant.py
│   ├── customer_support.py
│   └── research_assistant.py
├── requirements.txt             # Dependencies
├── setup.py                     # Installation script
├── README.md                    # Documentation
└── LICENSE                      # License file
```

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request with a detailed description of your changes.

## License
This project is licensed under the [MIT License](LICENSE).

## Support
For issues, feature requests, or questions, please open an issue in the repository or reach out to the team.

