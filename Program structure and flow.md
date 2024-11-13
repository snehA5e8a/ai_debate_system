debate_system/

├── base_agent.py
├── debate_agent.py
├── fact_checker.py
├── moderator.py
├── llm.py
└── utils.py

PROGRAM INITIALIZATION
-----------------------

1. main.py
   ├── Server Initialization
   │   ├── Sets up Streamlit interface
   │   └── Loads environment variables (API tokens)
   │
   ├── UI Components
   │   ├── Topic input field
   │   ├── Parameter selections:
   │   │   ├── Number of rounds
   │   │   ├── Fact checking toggle
   │   │   └── Debate style selection
   │   └── Start Debate button
   │
   ├── When "Start Debate" clicked
   │   ├── Creates LLM instance
   │   │   └── HFInferenceLLM(api_token)
   │   │
   │   ├── Initializes Agents directly
   │   │   ├── pro_debater = DebateAgent("Proponent", "in favor", llm), updates personality[confidence, adaptability]
   │   │   ├── con_debater = DebateAgent("Opponent", "against", llm)
   │   │   ├── fact_checker = FactCheckerAgent(llm)
   │   │   └── moderator = ModeratorAgent(llm)
   │   │
   │   └── Starts Debate Flow
   │       ├── moderator.moderate(topic, "introduction")
   │       │
   │       ├── Opening Phase
   │       │   ├── pro_opening = pro_debater.generate_opening_statement(topic, parameters)
   │       │   ├── fact_check = fact_checker.check_statement(pro_opening) if enabled
   │       │   ├── con_opening = con_debater.generate_opening_statement(topic, parameters)
   │       │   └── fact_check = fact_checker.check_statement(con_opening) if enabled
   │       │
   │       ├── Debate Rounds
   │       │   └── For each round:
   │       │       ├── pro_rebuttal = pro_debater.generate_rebuttal(topic, con_argument, parameters)
   │       │       ├── fact_check if enabled (statement - claim - verify claims - confidence)
   │       │       ├── con_rebuttal = con_debater.generate_rebuttal(topic, pro_argument, parameters)
   │       │       └── fact_check if enabled
   │       │       └── Analyze opponent argument
   │       │       └── Moderator intervention if required
   │       │
   │       └── Closing Phase
   │           ├── pro_closing = pro_debater.generate_closing_statement(topic, parameters)
   │           ├── con_closing = con_debater.generate_closing_statement(topic, parameters)
   │           └── moderator.moderate(topic, "closing")
   │
   └── UI Updates
       ├── Display current speaker
       ├── Show statements/rebuttals
       ├── Display fact-check results
       └── Show debate progress