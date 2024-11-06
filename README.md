# AI Debate System

## Project Structure
```plaintext
project_root/
├── .env                  # Contains API tokens and secrets
├── .gitignore           # Specifies which files Git should ignore
├── README.md            # Project documentation
├── requirements.txt     # Project dependencies
└── src/                 # Source code directory
    ├── __init__.py     # Makes src a Python package
    ├── main.py         # Main application entry point
    └── agents/         # Agent-related code
        ├── __init__.py # Makes agents a Python package
        ├── base_agent.py    # Base agent class definition
        ├── debate_agent.py  # Debate agent implementation
        └── llm.py          # Language model interface