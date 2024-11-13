Multi-layered hierarchical representation of Base agent
-------------------------------------------------------------

Core: Primary agent behaviors
Layer 1: Direct support for core functions
Layer 2: Processing and analysis
Layer 3: Utility and helper functions

Core Layer (Primary Agent Functions)
├── perceive(input_data) --> processed data, emotional response, current state
│   ├── Layer 1: Direct Support
│   │   ├── _process_input(input_data) --> structured info with type, content, metadata, extracted info
│   │   ├── _update_emotion(input_data) --> updates agent's emotion state
│   │   └── _store_memory(info) --> stores in memory, returns success status
│   │
│   ├── Layer 2: Processing Support
│   │   ├── _extract_key_information(input_data) --> main points, evidence, implications
│   │   ├── _is_important(info) --> boolean importance flag
│   │   └── _calculate_importance(info) --> importance score (0-1)
│   │
│   └── Layer 3: Analysis Support
│       ├── _has_emotional_significance(info) --> boolean emotional relevance
│       ├── _is_relevant_to_goals(info) --> boolean goal relevance
│       └── _clean_text(text) --> formatted text

├── decide(context) --> decision with best option and supporting data
│   ├── Layer 1: Decision Making
│   │   ├── _generate_options(context, memories, beliefs) --> list of possible actions with confidence scores
│   │   ├── _evaluate_options(options) --> best option with highest score
│   │   └── _calculate_decision_confidence(option) --> confidence score (0-1)
│   │
│   ├── Layer 2: Information Retrieval
│   │   ├── _retrieve_relevant_memories(context) --> list of relevant memories sorted by importance
│   │   ├── _get_relevant_beliefs(context) --> list of applicable beliefs
│   │   └── _calculate_context_match(memory_context, current_context) --> match score (0-1)
│   │
│   └── Layer 3: Relevance Checking
│       ├── _is_applicable(memory, context) --> boolean applicability
│       └── _is_belief_relevant(belief, context) --> boolean relevance

├── act(decision) --> action result, status, metrics
│   ├── Layer 1: Action Execution
│   │   ├── _execute_action(decision) --> action outcome
│   │   └── _get_action_metrics(result) --> performance metrics
│   │
│   ├── Layer 2: Validation
│   │   ├── _is_action_successful(result) --> boolean success status
│   │   └── _validate_input(input_data) --> validation status and errors
│   │
│   └── Layer 3: Documentation
│       ├── _format_response(response) --> formatted response
│       └── _log_activity(activity) --> logging confirmation

└── learn(feedback) --> updated agent state
    ├── Layer 1: Update Systems
    │   ├── _update_beliefs(feedback) --> updated beliefs status
    │   ├── _adapt_personality(feedback) --> modified personality traits
    │   └── _update_goals(feedback) --> updated goals progress
    │
    ├── Layer 2: Analysis Support
    │   ├── _calculate_evidence_likelihood(evidence) --> likelihood score (0-1)
    │   ├── _calculate_emotional_stability() --> stability score (0-1)
    │   └── _evaluate_goal_progress() --> progress metrics for each goal
    │
    └── Layer 3: Processing Support
        ├── _parse_verification_response(response) --> structured verification result
        ├── _prioritize_goals() --> ordered list of goals by priority
        └── _manage_memory_capacity() --> memory management status

State Management (Cross-cutting)
├── get_state() --> current agent state snapshot (all properties)
└── _update_state() --> confirmation of state update