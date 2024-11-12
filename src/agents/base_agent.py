from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import time
import numpy as np
from datetime import datetime

class AgentState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    LEARNING = "learning"
    ANALYZING = "analyzing"

class AgentEmotion(Enum):
    NEUTRAL = "neutral"
    ENGAGED = "engaged"
    DEFENSIVE = "defensive"
    PERSUASIVE = "persuasive"
    ANALYTICAL = "analytical"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"

@dataclass
class Belief:
    content: str
    confidence: float  # 0-1
    evidence: List[str]
    last_updated: float
    source: Optional[str] = None
    contradictions: List[str] = field(default_factory=list)

@dataclass
class Memory:
    content: str
    importance: float  # 0-1
    context: Dict
    timestamp: float
    type: str  # 'episodic' or 'semantic'
    associations: List[str] = field(default_factory=list)

@dataclass
class Goal:
    description: str
    priority: float  # 0-1
    progress: float  # 0-1
    deadline: Optional[float] = None
    subgoals: List['Goal'] = field(default_factory=list)
    achieved: bool = False

class BaseAgent:
    """
    Base agent class implementing core agentic properties:
    - Goals: Maintain and pursue objectives
    - Actions: Execute decisions based on state
    - Perception: Process and understand input
    - Memory: Store and retrieve information
    - Learning: Adapt behavior based on experience
    """
    def __init__(self, name: str, role: str, llm=None):
        # Basic properties
        self.name = name
        self.role = role
        self.llm = llm
        
        # Core agentic properties
        self.state = AgentState.IDLE
        self.emotion = AgentEmotion.NEUTRAL
        self.beliefs: List[Belief] = []
        self.memories: List[Memory] = []
        self.goals: List[Goal] = []
        
        # Performance tracking
        self.performance_metrics = {
            'decisions_made': 0,
            'successful_actions': 0,
            'learning_events': 0
        }
        
        # Personality traits (0-1 scale)
        self.personality = {
            'openness': np.random.uniform(0.5, 1.0),
            'confidence': np.random.uniform(0.6, 0.9),
            'aggressiveness': np.random.uniform(0.3, 0.7),
            'adaptability': np.random.uniform(0.5, 0.9)
        }
        
        # Initialize working memory
        self.working_memory = {
            'current_focus': None,
            'active_goals': [],
            'recent_inputs': []
        }
    
    def _is_important(self, info: Dict) -> bool:
        """Determine if information is important enough to store in memory"""
        importance_score = 0.0
        
        # Check content length (longer content might be more important)
        content = info.get('content', '')
        if isinstance(content, str):
            importance_score += min(len(content) / 1000, 0.3)  # Cap at 0.3
        
        # Check if contains evidence or data
        evidence_words = ['evidence', 'research', 'study', 'data', 'shows', 'proves']
        if any(word in str(content).lower() for word in evidence_words):
            importance_score += 0.2
            
        # Check relevance to current goals
        if self._is_relevant_to_goals(info):
            importance_score += 0.3
            
        # Check emotional significance
        if self._has_emotional_significance(info):
            importance_score += 0.2
            
        return importance_score > 0.5

    def _is_relevant_to_goals(self, info: Dict) -> bool:
        """Check if information is relevant to current goals"""
        content = str(info.get('content', '')).lower()
        
        for goal in self.goals:
            if not goal.achieved and goal.description.lower() in content:
                return True
                
        return False

    def _has_emotional_significance(self, info: Dict) -> bool:
        """Check if information has emotional significance"""
        emotional_words = {
            'positive': ['success', 'achievement', 'breakthrough', 'agreement'],
            'negative': ['failure', 'mistake', 'disagreement', 'conflict'],
            'important': ['critical', 'essential', 'crucial', 'vital']
        }
        
        content = str(info.get('content', '')).lower()
        
        for category in emotional_words.values():
            if any(word in content for word in category):
                return True
                
        return False

    def _extract_key_information(self, input_data: Dict) -> Dict:
        """Extract key information from input data"""
        if not input_data or not isinstance(input_data, dict):
            return {}
            
        content = input_data.get('content', '')
        if not content:
            return {}
            
        # Try to extract using LLM if available
        if self.llm:
            try:
                prompt = f"""Extract key information from this content:
                {content}
                
                Format as:
                - Main points:
                - Evidence:
                - Implications:
                """
                
                result = self.llm(prompt)
                return {
                    'extracted_content': result,
                    'timestamp': time.time(),
                    'source': input_data.get('source', 'unknown')
                }
            except Exception:
                pass
        
        # Fallback to basic extraction
        return {
            'content': content,
            'timestamp': time.time(),
            'source': input_data.get('source', 'unknown')
        }

    def _calculate_importance(self, info: Dict) -> float:
        """Calculate importance score for information"""
        base_score = 0.5
        
        # Content length factor
        content = str(info.get('content', ''))
        length_score = min(len(content) / 1000, 0.3)
        
        # Evidence factor
        evidence_words = ['evidence', 'research', 'study', 'data']
        evidence_score = 0.2 if any(word in content.lower() for word in evidence_words) else 0
        
        # Relevance to goals factor
        goals_score = 0.3 if self._is_relevant_to_goals(info) else 0
        
        # Emotional significance factor
        emotion_score = 0.2 if self._has_emotional_significance(info) else 0
        
        total_score = base_score + length_score + evidence_score + goals_score + emotion_score
        return min(total_score, 1.0)

    def _calculate_context_match(self, memory_context: Dict, current_context: Dict) -> float:
        """Calculate how well a memory's context matches current context"""
        if not memory_context or not current_context:
            return 0.0
            
        matching_keys = set(memory_context.keys()) & set(current_context.keys())
        if not matching_keys:
            return 0.0
            
        match_scores = []
        for key in matching_keys:
            if memory_context[key] == current_context[key]:
                match_scores.append(1.0)
            else:
                match_scores.append(0.3)  # Partial match
                
        return sum(match_scores) / len(matching_keys)

    def _is_applicable(self, memory: Memory, context: Dict) -> bool:
        """Determine if a memory is applicable to current context"""
        # Check if memory type matches context
        if context.get('type') and memory.type != context['type']:
            return False
            
        # Check if memory is recent enough
        if context.get('max_age'):
            age = time.time() - memory.timestamp
            if age > context['max_age']:
                return False
                
        # Check context matching score
        context_match = self._calculate_context_match(memory.context, context)
        return context_match > 0.5

    def _calculate_evidence_likelihood(self, evidence: Dict) -> float:
        """Calculate likelihood of evidence supporting a belief"""
        if not evidence:
            return 0.5  # Default uncertainty
            
        # Base factors
        strength_factors = {
            'direct_evidence': 0.8,
            'indirect_evidence': 0.4,
            'anecdotal': 0.2
        }
        
        # Get evidence type (default to anecdotal)
        evidence_type = evidence.get('type', 'anecdotal')
        base_strength = strength_factors.get(evidence_type, 0.2)
        
        # Adjust for confidence
        confidence = evidence.get('confidence', 0.5)
        
        # Adjust for recency
        age = time.time() - evidence.get('timestamp', time.time())
        recency_factor = np.exp(-age / (24 * 3600))  # Decay over 24 hours
        
        return base_strength * confidence * recency_factor

    def _calculate_emotional_stability(self) -> float:
        """Calculate emotional stability metric"""
        # Get recent emotional states
        recent_states = [m.context.get('emotion') for m in self.memories[-10:] 
                        if m.context.get('emotion')]
        
        if not recent_states:
            return 1.0  # Default stability
            
        # Calculate variance in emotional states
        unique_states = len(set(recent_states))
        stability = 1.0 - (unique_states / len(recent_states))
        
        return max(stability, 0.0)

    def _parse_verification_response(self, response: str) -> Dict:
        """Parse verification response from LLM"""
        try:
            lines = response.strip().split('\n')
            status = "Unverified"
            confidence = 0.0
            reason = ""
            
            for line in lines:
                if "status:" in line.lower():
                    status = line.split(':')[1].strip()
                elif "confidence:" in line.lower():
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except ValueError:
                        confidence = 0.5
                elif "reason:" in line.lower():
                    reason = line.split(':')[1].strip()
                    
            return {
                'status': status,
                'confidence': confidence,
                'reason': reason
            }
        except Exception:
            return {
                'status': "Error",
                'confidence': 0.0,
                'reason': "Failed to parse verification response"
            }

    def perceive(self, input_data: Dict) -> Dict:
        """Process and understand incoming information"""
        self.state = AgentState.LISTENING
        
        # Update working memory with new input
        self.working_memory['recent_inputs'].append({
            'content': input_data,
            'timestamp': time.time()
        })
        
        # Extract relevant information
        extracted_info = self._process_input(input_data)
        
        # Update emotional state based on input
        self._update_emotion(input_data)
        
        # Store in memory if important
        if self._is_important(extracted_info):
            self._store_memory(extracted_info)
        
        return {
            'processed_data': extracted_info,
            'emotional_response': self.emotion.value,
            'current_state': self.state.value
        }

    def decide(self, context: Dict) -> Dict:
        """Make decisions based on current state and goals"""
        self.state = AgentState.THINKING
        
        # Get relevant memories and beliefs
        relevant_memories = self._retrieve_relevant_memories(context)
        relevant_beliefs = self._get_relevant_beliefs(context)
        
        # Evaluate options based on goals and context
        options = self._generate_options(context, relevant_memories, relevant_beliefs)
        best_option = self._evaluate_options(options)
        
        # Update performance metrics
        self.performance_metrics['decisions_made'] += 1
        
        return {
            'decision': best_option,
            'supporting_data': {
                'memories_used': relevant_memories,
                'beliefs_considered': relevant_beliefs,
                'options_evaluated': options
            },
            'confidence': self._calculate_decision_confidence(best_option)
        }

    def act(self, decision: Dict) -> Dict:
        """Execute actions based on decisions"""
        self.state = AgentState.SPEAKING
        
        try:
            # Execute the decided action
            result = self._execute_action(decision)
            
            # Update performance metrics
            if self._is_action_successful(result):
                self.performance_metrics['successful_actions'] += 1
            
            return {
                'action_result': result,
                'status': 'success',
                'metrics': self._get_action_metrics(result)
            }
        except Exception as e:
            return {
                'action_result': None,
                'status': 'failure',
                'error': str(e)
            }

    def learn(self, feedback: Dict):
        """Update internal state based on feedback"""
        self.state = AgentState.LEARNING
        
        # Update beliefs based on feedback
        self._update_beliefs(feedback)
        
        # Adjust personality traits
        self._adapt_personality(feedback)
        
        # Update goals if necessary
        self._update_goals(feedback)
        
        # Track learning event
        self.performance_metrics['learning_events'] += 1

    def _process_input(self, input_data: Dict) -> Dict:
        """Extract and structure information from input"""
        if not input_data:
            return {}
            
        try:
            return {
                'type': input_data.get('type', 'unknown'),
                'content': input_data.get('content', ''),
                'metadata': {
                    'timestamp': time.time(),
                    'source': input_data.get('source', 'unknown'),
                    'context': input_data.get('context', {})
                },
                'extracted_info': self._extract_key_information(input_data)
            }
        except Exception as e:
            return {'error': str(e)}

    def _update_emotion(self, input_data: Dict):
        """Update emotional state based on input"""
        # Analyze input content
        content = input_data.get('content', '')
        
        # Simple emotion mapping based on content
        if any(word in content.lower() for word in ['disagree', 'wrong', 'incorrect']):
            self.emotion = AgentEmotion.DEFENSIVE
        elif any(word in content.lower() for word in ['evidence', 'data', 'research']):
            self.emotion = AgentEmotion.ANALYTICAL
        elif any(word in content.lower() for word in ['agree', 'support', 'correct']):
            self.emotion = AgentEmotion.CONFIDENT
        else:
            self.emotion = AgentEmotion.NEUTRAL

    def _store_memory(self, info: Dict):
        """Store information in memory"""
        memory = Memory(
            content=info['content'],
            importance=self._calculate_importance(info),
            context=info['metadata'],
            timestamp=time.time(),
            type='episodic' if info['type'] == 'event' else 'semantic'
        )
        self.memories.append(memory)
        
        # Prune old, unimportant memories if needed
        self._manage_memory_capacity()

    def _retrieve_relevant_memories(self, context: Dict) -> List[Memory]:
        """Get memories relevant to current context"""
        relevant_memories = []
        current_time = time.time()
        
        for memory in self.memories:
            # Calculate relevance score
            time_factor = np.exp(-(current_time - memory.timestamp) / 3600)
            context_match = self._calculate_context_match(memory.context, context)
            relevance = time_factor * context_match * memory.importance
            
            if relevance > 0.5:  # Threshold for relevance
                relevant_memories.append(memory)
        
        return sorted(relevant_memories, key=lambda m: m.importance, reverse=True)

    def _get_relevant_beliefs(self, context: Dict) -> List[Belief]:
        """Get beliefs relevant to current context"""
        return [b for b in self.beliefs if self._is_belief_relevant(b, context)]

    def _generate_options(self, context: Dict, memories: List[Memory], beliefs: List[Belief]) -> List[Dict]:
        """Generate possible action options"""
        options = []
        
        # Generate options based on context and memory
        for memory in memories:
            if self._is_applicable(memory, context):
                options.append({
                    'action': 'apply_past_experience',
                    'data': memory,
                    'confidence': memory.importance
                })
        
        # Generate options based on beliefs
        for belief in beliefs:
            if belief.confidence > 0.7:  # Threshold for using beliefs
                options.append({
                    'action': 'apply_belief',
                    'data': belief,
                    'confidence': belief.confidence
                })
        
        return options

    def _evaluate_options(self, options: List[Dict]) -> Dict:
        """Evaluate and select best option"""
        if not options:
            return {'action': 'default', 'confidence': 0.5}
        
        # Score each option
        scored_options = []
        for option in options:
            score = option['confidence']
            # Adjust score based on personality
            score *= (1 + self.personality['confidence'] - 0.5)
            scored_options.append((score, option))
        
        # Return option with highest score
        return max(scored_options, key=lambda x: x[0])[1]

    def _manage_memory_capacity(self, max_memories: int = 1000):
        """Manage memory capacity by removing least important memories"""
        if len(self.memories) > max_memories:
            # Sort by importance and keep top memories
            self.memories.sort(key=lambda m: m.importance)
            self.memories = self.memories[-max_memories:]

    def _update_beliefs(self, feedback: Dict):
        """Update beliefs based on feedback"""
        for belief in self.beliefs:
            if belief.content in feedback.get('confirmed_facts', []):
                belief.confidence = min(belief.confidence + 0.1, 1.0)
            elif belief.content in feedback.get('contradicted_facts', []):
                belief.confidence = max(belief.confidence - 0.1, 0.0)

    def _adapt_personality(self, feedback: Dict):
        """Adapt personality traits based on feedback"""
        success = feedback.get('success', False)
        
        # Adjust confidence based on success
        if success:
            self.personality['confidence'] = min(
                self.personality['confidence'] + 0.05,
                1.0
            )
        else:
            self.personality['confidence'] = max(
                self.personality['confidence'] - 0.05,
                0.0
            )
            
        # Adjust adaptability
        self.personality['adaptability'] = min(
            self.personality['adaptability'] + 0.02,
            1.0
        )

    def _update_goals(self, feedback: Dict):
        """Update goals based on feedback"""
        # Update progress on existing goals
        for goal in self.goals:
            if goal.description in feedback.get('achieved_goals', []):
                goal.achieved = True
                goal.progress = 1.0
            elif 'goal_progress' in feedback:
                goal.progress = min(goal.progress + 0.1, 1.0)

    def get_state(self) -> Dict:
        """Get current agent state"""
        return {
            'name': self.name,
            'role': self.role,
            'state': self.state.value,
            'emotion': self.emotion.value,
            'personality': self.personality,
            'performance': self.performance_metrics,
            'active_goals': [g for g in self.goals if not g.achieved],
            'working_memory': self.working_memory
        }