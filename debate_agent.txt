DEBATE AGENTS

When DebateAgent generates content:
   1. perceive() - Analyzes context
   2. decide() - Plans response
   3. act() - Generates content using LLM
   4. learn() - Updates based on feedback

DebateAgent (Inherits from BaseAgent)
├── Core Debate Functions
│   ├── generate_opening_statement(topic, parameters) 
│   │   ├── Input: topic, style, time limits
│   │   ├── Output: opening statement, confidence, metadata
│   │   └── Purpose: Creates initial position and arguments
│   │
│   ├── generate_rebuttal(topic, opponent_argument, parameters)
│   │   ├── Input: opponent's argument, debate context, time limit
│   │   ├── Output: counter-arguments, addressed points, confidence
│   │   └── Purpose: Responds to opponent's points with counter-arguments
│   │
│   └── generate_closing_statement(topic, parameters)
│       ├── Input: debate history, key points made, time limit
│       ├── Output: closing statement, summary, confidence
│       └── Purpose: Summarizes position and reinforces main points

├── Layer 1: Argument Analysis
│   ├── _analyze_opponent_argument(argument)
│   │   ├── Input: opponent's statement
│   │   ├── Output: main claims, evidence, weaknesses, counter-points
│   │   └── Purpose: Breaks down opponent's argument for rebuttal
│   │
│   ├── _evaluate_argument_strength(argument)
│   │   ├── Input: argument content
│   │   ├── Output: strength score (0-1)
│   │   └── Purpose: Assesses argument quality and effectiveness
│   │
│   └── _analyze_debate_history()
│       ├── Input: stored debate events
│       ├── Output: key points, consistency score, argument patterns
│       └── Purpose: Reviews debate progression for strategy

├── Layer 2: Content Generation
│   ├── _create_opening_prompt(topic, perception)
│   │   ├── Input: topic, context, style
│   │   ├── Output: structured prompt for LLM
│   │   └── Purpose: Formats prompt for opening statement
│   │
│   ├── _create_rebuttal_prompt(topic, analysis, counter_points)
│   │   ├── Input: opponent analysis, counter-points
│   │   ├── Output: structured prompt for rebuttal
│   │   └── Purpose: Prepares rebuttal generation prompt
│   │
│   ├── _create_closing_prompt(topic, analysis)
│   │   ├── Input: debate summary, key points
│   │   ├── Output: structured prompt for closing
│   │   └── Purpose: Formats closing statement prompt
│   │
│   └── _generate_argument(prompt, style, constraints)
│       ├── Input: prepared prompt, debate style, limitations
│       ├── Output: formatted argument content
│       └── Purpose: Core argument generation using LLM

├── Layer 3: Evidence & Claims
│   ├── _extract_claims(text)
│   │   ├── Input: argument text
│   │   ├── Output: list of key claims
│   │   └── Purpose: Identifies main argument points
│   │
│   ├── _extract_evidence(text)
│   │   ├── Input: argument text
│   │   ├── Output: supporting evidence list
│   │   └── Purpose: Finds evidence in arguments
│   │
│   ├── _extract_counter_points(text)
│   │   ├── Input: analyzed text
│   │   ├── Output: potential counter-arguments
│   │   └── Purpose: Identifies points to counter
│   │
│   └── _extract_weaknesses(text)
│       ├── Input: argument text
│       ├── Output: list of logical weaknesses
│       └── Purpose: Identifies flaws in arguments

└── Layer 4: Debate Support
    ├── _generate_completion(partial_response, topic)
    │   ├── Input: incomplete response, context
    │   ├── Output: completed argument
    │   └── Purpose: Ensures complete arguments
    │
    ├── _calculate_confidence(argument)
    │   ├── Input: argument, evidence
    │   ├── Output: confidence score
    │   └── Purpose: Assesses argument reliability
    │
    ├── _evaluate_stance_consistency(arguments)
    │   ├── Input: list of arguments
    │   ├── Output: consistency score
    │   └── Purpose: Checks position consistency
    │
    ├── _generate_counter_points(analysis)
    │   ├── Input: opponent argument analysis
    │   ├── Output: prioritized counter-points
    │   └── Purpose: Plans rebuttal strategy
    │
    └── _parse_argument_feedback(feedback)
        ├── Input: debate feedback
        ├── Output: structured feedback analysis
        └── Purpose: Processes feedback for learning


Data Flow 
------------


1. Opening Statement Flow:
	1. Topic & Parameters → perceive()
	2. Topic Analysis → _extract_key_information()
	3. Context → _create_opening_prompt()
	4. Prompt → _generate_argument()
	5. Raw Content → _extract_claims()
	6. Claims → _extract_evidence()
	7. Content & Evidence → _evaluate_argument_strength()
	8. Final Opening with:
	   ├── Main statement
	   ├── Evidence support
	   ├── Confidence score
	   └── Metadata (stance, style)

2. Rebuttal Flow:
	1. Opponent Argument → _analyze_opponent_argument()
	2. Analysis → _extract_claims(), _extract_weaknesses()
	3. Claims & Weaknesses → _generate_counter_points()
	4. Counter Points → _create_rebuttal_prompt()
	5. Prompt → _generate_argument()
	6. Generated Content → _evaluate_argument_strength()
	7. Final Rebuttal with:
	   ├── Counter arguments
	   ├── Addressed points
	   ├── Confidence score
	   └── Response strategy

3. Closing Statement Flow:
	1. Debate History → _analyze_debate_history()
	2. History Analysis → 
	   ├── _extract_key_points()
	   └── _evaluate_stance_consistency()
	3. Analysis Results → 
	   ├── _summarize_main_arguments()
	   └── _identify_strongest_points()
	4. Summary → _create_closing_prompt()
	5. Prompt → _generate_argument()
	6. Generated Content → 
	   ├── _evaluate_argument_strength()
	   └── _calculate_confidence()
	7. Final Closing with:
	   ├── Key points summary
	   ├── Position reinforcement
	   ├── Confidence score
	   └── Debate effectiveness metrics

1. Initial Analysis Phase
   ├── Context understanding
   └── Information extraction

2. Content Planning
   ├── Strategy selection
   └── Prompt creation

3. Generation Phase
   ├── LLM interaction
   └── Content structuring

4. Evaluation Phase
   ├── Strength assessment
   └── Confidence scoring