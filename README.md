# AI Debate System

An agentic adversarial AI debate system that facilitates structured debates between AI agents on various topics with moderation and fact-checking capabilities.

Check the app here: https://aidebatesystem-s4dzbsqmfvpsalgpjfgl3j.streamlit.app/

## Project Structure
```
ai_debate_system/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── debate_agent.py
│   │   ├── debate_system.py
│   │   ├── fact_checker.py
│   │   ├── llm.py
│   │   └── moderator.py
│   ├── env/
│   └── main.py
├── requirements.txt
└── README.md
```

## Description

This system implements an AI-powered debate platform where two AI agents engage in structured debates on user-specified topics. The system includes:
- Debate agents that can argue for and against positions
- A fact-checker to verify claims
- A moderator to guide the debate
- Integration with HuggingFace's language models

## Features

- Multiple debate styles (Formal, Casual, Academic)
- Real-time fact checking
- Structured debate format with opening statements, rebuttals, and closing arguments
- Content validation for appropriate discourse
- Detailed debate statistics and analysis
- Customizable debate parameters
- Streamlit-based user interface

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_debate_system
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Get a HuggingFace API token from https://huggingface.co/settings/tokens

## Usage

1. Run the application:
```bash
streamlit run src/main.py
```

2. Enter your HuggingFace API token when prompted

3. Configure debate parameters:
   - Select a debate topic
   - Choose debate style
   - Set number of rounds
   - Enable/disable fact checking
   - Adjust other parameters as needed

4. Click "Start Debate" to begin

## Components

### DebateAgent
- Manages individual debater behavior
- Generates arguments and rebuttals
- Adapts strategy based on opponent's arguments

### FactChecker
- Verifies claims made during debate
- Provides fact-check ratings
- Maintains verification history

### Moderator
- Guides debate flow
- Ensures balanced participation
- Provides transitions between stages

### DebateSystem
- Orchestrates overall debate
- Manages agent interactions
- Handles content validation
- Tracks debate progress

## Configuration

The system supports various parameters that can be adjusted through the UI:
- Debate style (Formal/Casual/Academic)
- Number of exchange rounds (1-5)
- Points per argument (1-5)
- Fact checking toggle
- Agent thinking process visibility

## Dependencies

- streamlit
- huggingface_hub
- python-dotenv
- (See requirements.txt for complete list)

## Development

To contribute to the project:
1. Create a new branch
2. Make your changes
3. Run tests (if available)
4. Submit a pull request

## Notes

- The system uses HuggingFace's Zephyr-7b-beta model
- Requires active internet connection
- Performance depends on API response times
- Content validation is implemented for appropriate discourse

## Future Improvements

- Additional debate formats
- Enhanced fact-checking capabilities
- More sophisticated argument analysis
- Extended content validation
- Support for multiple language models
- Integration with other AI platforms

## License

All rights reserved. This project is currently unlicensed.
Note: Without a license:

The code is under exclusive copyright by default
No one can copy, distribute, or modify your work
No one can use your code for public or commercial purposes
Others can read and learn from your code, but cannot use it in their own projects

If you plan to collaborate or share this project in the future, consider adding an open-source license.

## Authors

* Sneha Sebastian - Initial work - [snehA5e8a](https://github.com/snehA5e8a)
