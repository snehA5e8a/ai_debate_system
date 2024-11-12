# AI Debate System: Agentic Framework Design Document

## 1. System Overview

The AI Debate System implements an agentic framework where multiple autonomous AI agents collaborate to conduct structured debates. The system utilizes the HuggingFace Inference API with the Zephyr-7b-beta model for natural language processing capabilities.

## 2. Agent Architecture

### 2.1 Core Agent Components
Each agent in the system follows a common agentic structure with five key properties:
- **Goals**: Specific objectives driving agent behavior
- **Actions**: Available operations the agent can perform
- **Perception**: Ability to analyze and understand context
- **Memory**: Storage of historical information and learned patterns
- **Learning**: Adaptation mechanisms based on experience

### 2.2 Agent Types

#### 2.2.1 Debate Agent (DebateAgent)
- **Purpose**: Present and defend assigned viewpoints in debates
- **Properties**:
  ```python
  {
    "name": "string",
    "stance": "string (in favor/against)",
    "memory": "list of past arguments",
    "strategy": "string (balanced/aggressive/defensive)",
    "stats": {
      "arguments_made": "integer",
      "rebuttals_made": "integer",
      "points_addressed": "integer"
    }
  }
  ```
- **Key Methods**:
  - `generate_opening_statement(topic, parameters)`
  - `generate_rebuttal(topic, opponent_argument, parameters)`
  - `generate_closing_statement(topic, parameters)`
  - `analyze_opponent(argument)`
  - `remember(content, type)`

#### 2.2.2 Fact Checker Agent (FactCheckerAgent)
- **Purpose**: Ensure factual accuracy of debate content
- **Properties**:
  ```python
  {
    "verified_facts": "dictionary of checked statements",
    "verification_history": "list of past verifications"
  }
  ```
- **Key Methods**:
  - `check_facts(statement)`
  - Track verification history with timestamps

#### 2.2.3 Moderator Agent (ModeratorAgent)
- **Purpose**: Guide debate flow and maintain order
- **Properties**:
  ```python
  {
    "debate_history": "list of moderation actions"
  }
  ```
- **Key Methods**:
  - `moderate(topic, stage)`
  - Different moderation styles for introduction, transition, and closing

## 3. System Architecture

### 3.1 Core System (DebateSystem)
- **Main Components**:
  ```python
  {
    "topic": "debate topic",
    "parameters": "debate configuration",
    "debater_pro": "DebateAgent instance",
    "debater_con": "DebateAgent instance",
    "fact_checker": "FactCheckerAgent instance",
    "moderator": "ModeratorAgent instance",
    "debate_log": "list of debate events"
  }
  ```

### 3.2 Interaction Flow
1. System Initialization:
   ```mermaid
   graph TD
      A[User Input] --> B[Parameter Setup]
      B --> C[Agent Initialization]
      C --> D[Debate Start]
   ```

2. Debate Round Flow:
   ```mermaid
   graph TD
      A[Moderator Introduction] --> B[Opening Statements]
      B --> C[Main Arguments]
      C --> D[Rebuttals]
      D --> E[Closing Statements]
      E --> F[Moderator Closing]
      B & C & D --> G[Fact Checking]
   ```

## 4. Agent Decision Making

### 4.1 Debate Agent Strategy
- Analyzes opponent arguments using structured prompts
- Adapts tone and approach based on debate parameters
- Maintains memory of previous points for coherent arguments
- Validates content against inappropriate terms

### 4.2 Fact Checker Process
- Identifies specific, verifiable claims
- Rates claims with confidence levels
- Provides supporting evidence
- Notes missing context or biases

### 4.3 Moderator Controls
- Guides debate progression through stages
- Maintains neutrality while ensuring flow
- Provides appropriate transitions
- Summarizes key points

## 5. Implementation Details

### 5.1 Language Model Interface
```python
class HFInferenceLLM:
    - Initialization with API token
    - Text generation with parameters:
        - max_new_tokens=256
        - temperature=0.7
        - repetition_penalty=1.1
```

### 5.2 Content Validation
- Checks for inappropriate terms:
  ```python
  inappropriate_terms = [
      "violent", "abusive", "hate", "discriminatory",
      "threatening", "explicit", "offensive"
  ]
  ```

### 5.3 Debate Parameters
- Configurable options:
  ```python
  parameters = {
      'debate_style': ["Formal", "Casual", "Academic"],
      'debate_rounds': 1-5,
      'focus_points': 1-5,
      'fact_checking': boolean,
      'show_thinking': boolean
  }
  ```

## 6. Future Enhancements

### 6.1 Planned Improvements
- Enhanced agent learning capabilities
- More sophisticated fact-checking algorithms
- Dynamic strategy adaptation
- Real-time audience interaction
- Expanded content filtering

### 6.2 Performance Metrics
- Track debate quality metrics
- Monitor fact-checking accuracy
- Measure agent adaptation effectiveness
- Evaluate content appropriateness

## 7. Usage Guidelines

### 7.1 System Requirements
- HuggingFace API access
- Streamlit for UI
- Python 3.7+
- Required libraries:
  - huggingface_hub
  - streamlit
  - time
  - typing
  - json

### 7.2 Setup Instructions
1. Install dependencies
2. Configure HuggingFace API token
3. Launch Streamlit interface
4. Configure debate parameters
5. Input debate topic
6. Start debate session

## 8. Security and Safety

### 8.1 Content Filtering
- Real-time content validation
- Inappropriate term detection
- Civil discourse enforcement

### 8.2 API Security
- Secure token handling
- Rate limiting
- Error handling

## 9. Monitoring and Logging

### 9.1 Event Logging
- Detailed debate logs
- Agent action tracking
- System performance metrics

### 9.2 Debug Information
- Real-time agent thinking display
- Progress tracking
- Error reporting
