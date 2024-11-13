1. BaseAgent Parameters:
├── Instance Parameters (self):
│   ├── role: str            # Agent's role/function
│   ├── llm: LLMInterface    # Language model instance
│   │
│   ├── state: AgentState    # Current operational state
│   │   └── Enum: IDLE, LISTENING, THINKING, SPEAKING
│   │
│   ├── emotion: AgentEmotion # Current emotional state
│   │   └── Enum: NEUTRAL, ENGAGED, DEFENSIVE, PERSUASIVE, ANALYTICAL
│   │
│   ├── beliefs: List[Belief] # Knowledge & opinions
│   ├── memories: List[Memory]# Stored experiences
│   │
│   ├── performance_metrics: Dict
│   │   ├── decisions_made: int
│   │   ├── successful_actions: int
│   │   └── learning_events: int
│   │
│   ├── personality: Dict     # Trait scores (0-1)
│   │   ├── openness: float
│   │   ├── confidence: float
│   │   ├── aggressiveness: float
│   │   └── adaptability: float
│   │
│   └── working_memory: Dict
│       ├── current_focus: Any
│       ├── active_goals: List
│       └── recent_inputs: List

2. DebateAgent Parameters (extends BaseAgent):
├── Instance Parameters:
│   ├── [All BaseAgent parameters] +
│   ├── stance: str          # "in favor" or "against"
│   ├── style: DebateStyle   # FORMAL, CASUAL, ACADEMIC
│   ├── arguments_made: List[Argument]
│   ├── opponent_arguments: List[str]
│   │
│   └── personality additions:
│       ├── persuasiveness: float
│       ├── logical_reasoning: float
│       ├── emotional_appeal: float
│       └── adaptability: float
│
└── Argument Parameters:
    ├── content: str
    ├── strength: float
    ├── evidence: List[str]
    ├── type: str           # 'opening', 'rebuttal', 'closing'
    └── counter_points: List[str]

3. FactCheckerAgent Parameters (extends BaseAgent):
├── Instance Parameters:
│   ├── [All BaseAgent parameters] +
│   ├── verified_facts: Dict # Stored verifications
│   │
│   ├── confidence_thresholds: Dict
│   │   ├── high: float   # 0.8
│   │   ├── medium: float # 0.6
│   │   └── low: float    # 0.4
│   │
│   └── goals additions:
│       ├── verify_factual_accuracy: Goal
│       └── identify_misleading_statements: Goal

4. ModeratorAgent Parameters (extends BaseAgent):
├── Instance Parameters:
│   ├── [All BaseAgent parameters] +
│   │
│   ├── debate_state: Dict
│   │   ├── topic: str
│   │   ├── current_stage: str
│   │   ├── speaker_order: List[str]
│   │   ├── time_tracking: Dict
│   │   ├── interventions_made: List
│   │   ├── speaker_times: Dict
│   │   ├── last_speaker_start: float
│   │   ├── inappropriate_content_count: int
│   │   ├── interruptions: int
│   │   └── topic_adherence_score: float
│   │
│   ├── time_limits: Dict
│   │   ├── opening: int    # 180s
│   │   ├── rebuttal: int   # 120s
│   │   └── closing: int    # 180s
│   │
│   └── goals additions:
│       ├── ensure_fair_debate: Goal
│       └── maintain_productive_discussion: Goal

Shared Data Structures:
1. Belief:
├── content: str
├── confidence: float
├── evidence: List[str]
├── last_updated: float
├── source: Optional[str]
└── contradictions: List[str]

2. Memory:
├── content: str
├── importance: float
├── context: Dict
├── timestamp: float
├── type: str          # 'episodic' or 'semantic'
└── associations: List[str]

3. Goal:
├── description: str
├── priority: float
├── progress: float
├── deadline: Optional[float]
├── subgoals: List[Goal]
└── achieved: bool

Inheritance Structure:

All agents inherit BaseAgent parameters
Each adds specialized parameters
Maintains consistent base functionality


Parameter Types:

Configuration (name, role, style)
State tracking (state, emotion)
Performance (metrics, scores)
Memory (beliefs, memories)
Control (time_limits, thresholds)


Unique Features:

DebateAgent: Argument tracking, stance
FactChecker: Verification storage, confidence
Moderator: Debate state, time management