from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import numpy as np
from .base_agent import BaseAgent, AgentState, AgentEmotion, Memory, Belief, Goal

class DebateStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    ACADEMIC = "academic"

@dataclass
class Argument:
    content: str
    strength: float  # 0-1
    evidence: List[str]
    type: str  # 'opening', 'rebuttal', 'closing'
    counter_points: List[str]

class DebateAgent(BaseAgent):
    """Specialized agent for debate participation"""
    def __init__(self, name: str, stance: str, llm, style: DebateStyle = DebateStyle.FORMAL):
        super().__init__(name=name, role="debater", llm=llm)
        self.stance = stance
        self.style = style
        self.arguments_made: List[Argument] = []
        self.opponent_arguments: List[str] = []
        
        # Debate-specific personality traits
        self.personality.update({
            'persuasiveness': np.random.uniform(0.6, 0.9),
            'logical_reasoning': np.random.uniform(0.7, 0.95),
            'emotional_appeal': np.random.uniform(0.4, 0.8),
            'adaptability': np.random.uniform(0.6, 0.9)
        })
        
        # Initialize debate-specific goals
        self.goals.append(Goal(
            description="Present compelling arguments",
            priority=0.9,
            progress=0.0
        ))
        self.goals.append(Goal(
            description="Counter opponent arguments",
            priority=0.8,
            progress=0.0
        ))

    def generate_opening_statement(self, topic: str, parameters: Dict) -> Dict:
        """Generate opening debate statement"""
        try:
            # Perceive topic and context
            perception = self.perceive({
                'type': 'topic',
                'content': topic,
                'context': parameters
            })
            
            # Create prompt with clear length guidance
            prompt = f"""Generate a complete opening debate statement on: {topic}
            Position: {self.stance}
            
            Requirements:
            - Clear introduction, main points, and conclusion
            - Minimum 3 well-developed paragraphs
            - Strong, complete sentences
            - Professional debate tone
            - Present compelling evidence
            - Maximum 500 words
            - Each point should be fully explained
            - End with a complete sentence
            """
            
            response = self.llm(prompt)
            
            # Verify response length and completeness
            if len(response.split()) < 50:  # Minimum word count
                completion = self._generate_completion(response, topic)
                response = f"{response} {completion}".strip()
                
            argument = Argument(
                content=str(response),
                strength=self._evaluate_argument_strength(response),
                evidence=self._extract_evidence(response),
                type='opening',
                counter_points=[]
            )
            
            self.arguments_made.append(argument)
            
            return {
                'content': str(response),
                'metadata': {
                    'stance': self.stance,
                    'style': self.style.value,
                    'confidence': self._calculate_confidence(argument)
                }
            }
        except Exception as e:
            print(f"Error in generate_opening_statement: {str(e)}")  # Debug print
            return {
                'content': f"Error generating opening statement: {str(e)}",
                'metadata': {
                    'stance': self.stance,
                    'style': self.style.value,
                    'confidence': 0.0
                }
            }
    
    def generate_rebuttal(self, topic: str, opponent_argument: str, parameters: Dict) -> Dict:
        """Generate rebuttal to opponent's argument"""
        try:
            # Analyze opponent's argument
            analysis = self._analyze_opponent_argument(opponent_argument)
            
            # Update state with opponent's argument
            self.opponent_arguments.append(opponent_argument)
            
            # Generate counter-arguments
            counter_points = self._generate_counter_points(analysis)
            
            # Formulate rebuttal
            prompt = self._create_rebuttal_prompt(topic, analysis, counter_points)
            
            response = self.llm(prompt)
            
            argument = Argument(
                content=str(response),
                strength=self._evaluate_argument_strength(response),
                evidence=self._extract_evidence(response),
                type='rebuttal',
                counter_points=counter_points
            )
            
            self.arguments_made.append(argument)
            
            return {
                'content': str(response),
                'metadata': {
                    'points_addressed': counter_points,
                    'style': self.style.value,
                    'confidence': self._calculate_confidence(argument)
                }
            }
        except Exception as e:
            return {
                'content': f"Error generating rebuttal: {str(e)}",
                'metadata': {
                    'points_addressed': [],
                    'style': self.style.value,
                    'confidence': 0.0
                }
            }

    def generate_closing_statement(self, topic: str, parameters: Dict) -> Dict:
        """Generate closing statement"""
        try:
            # Analyze debate history
            debate_analysis = self._analyze_debate_history()
            
            # Create prompt with completion requirements
            prompt = f"""Generate a complete closing statement for the debate on: {topic}
            
            Key points made:
            {debate_analysis.get('key_points', [])}
            
            Requirements:
            - Summarize main arguments effectively
            - Address key counterpoints
            - Reinforce strongest evidence
            - Provide clear conclusion
            - Maximum 300 words
            - End with a powerful closing sentence
            - Complete all thoughts
            """
            
            response = self.llm(prompt)
            
            # Verify response completeness
            if len(response.split()) < 30:  # Minimum word count for closing
                completion = self._generate_completion(response, topic)
                response = f"{response} {completion}".strip()
            
            argument = Argument(
                content=str(response),
                strength=self._evaluate_argument_strength(response),
                evidence=self._extract_evidence(response),
                type='closing',
                counter_points=[]
            )
            
            self.arguments_made.append(argument)
            
            return {
                'content': str(response),
                'metadata': {
                    'key_points': debate_analysis.get('key_points', []),
                    'style': self.style.value,
                    'confidence': self._calculate_confidence(argument)
                }
            }
        except Exception as e:
            print(f"Error in generate_closing_statement: {str(e)}")  # Debug print
            return {
                'content': f"Error generating closing statement: {str(e)}",
                'metadata': {
                    'key_points': [],
                    'style': self.style.value,
                    'confidence': 0.0
                }
            }

    def _analyze_opponent_argument(self, argument: str) -> Dict:
        """Analyze opponent's argument for weaknesses and points to address"""
        if not argument or not isinstance(argument, str):
            return {
                'main_claims': [],
                'evidence': [],
                'weaknesses': [],
                'counter_points': []
            }

        prompt = f"""Analyze this argument and extract:
        1. Main claims made
        2. Evidence provided
        3. Logical weaknesses
        4. Potential counter-arguments

        Argument: {argument}
        """
        
        try:
            analysis = self.llm(prompt)
            return {
                'main_claims': self._extract_claims(str(analysis)),
                'evidence': self._extract_evidence(str(analysis)),
                'weaknesses': self._extract_weaknesses(str(analysis)),
                'counter_points': self._extract_counter_points(str(analysis))
            }
        except Exception:
            return {
                'main_claims': [],
                'evidence': [],
                'weaknesses': [],
                'counter_points': []
            }

    def _create_opening_prompt(self, topic: str, perception: Dict) -> str:
        """Create prompt for opening statement"""
        style_guide = {
            DebateStyle.FORMAL: "use formal language and structured arguments",
            DebateStyle.CASUAL: "use conversational tone while maintaining clarity",
            DebateStyle.ACADEMIC: "use academic language with research citations"
        }
        
        return f"""Generate an opening statement for a debate on: {topic}
        Position: {self.stance}
        Style: {style_guide[self.style]}
        
        Requirements:
        - Clear position statement
        - Strong supporting evidence
        - Logical flow
        - Appropriate tone for {self.style.value} style
        - Maximum 3 main points
        - No meta-text or explanations
        """

    def _create_rebuttal_prompt(self, topic: str, analysis: Dict, counter_points: List[str]) -> str:
        """Create prompt for rebuttal"""
        return f"""Generate a rebuttal for the debate on: {topic}
        Position: {self.stance}
        
        Address these points:
        {counter_points}
        
        Requirements:
        - Direct responses to opponent's claims
        - New supporting evidence
        - Clear logical arguments
        - {self.style.value} debate style
        - No meta-text or explanations
        - Complete all thoughts and sentences
        - Maximum 400 words
        - End with a strong conclusion
        """

    def _create_closing_prompt(self, topic: str, analysis: Dict) -> str:
        """Create prompt for closing statement"""
        return f"""Generate a closing statement for the debate on: {topic}
        Position: {self.stance}
        
        Key points made:
        {analysis.get('key_points', [])}
        
        Requirements:
        - Summarize main arguments
        - Reinforce key evidence
        - Address main counterpoints
        - Strong conclusion
        - {self.style.value} debate style
        - No meta-text or explanations
        - Maximum 300 words
        - Complete all thoughts and sentences
        """
    def generate_closing_statement(self, topic: str, parameters: Dict) -> Dict:
        """Generate closing statement"""
        try:
            # Analyze debate history
            debate_analysis = self._analyze_debate_history()
            
            # Create prompt with completion requirements
            prompt = f"""Generate a complete closing statement for the debate on: {topic}
            
            Key points made:
            {debate_analysis.get('key_points', [])}
            
            Requirements:
            - Summarize main arguments effectively
            - Address key counterpoints
            - Reinforce strongest evidence
            - Provide clear conclusion
            - Maximum 300 words
            - End with a powerful closing sentence
            - Complete all thoughts
            """
            
            response = self.llm(prompt)
            
            # Verify response completeness
            if len(response.split()) < 30:  # Minimum word count for closing
                completion = self._generate_completion(response, topic)
                response = f"{response} {completion}".strip()
            
            argument = Argument(
                content=str(response),
                strength=self._evaluate_argument_strength(response),
                evidence=self._extract_evidence(response),
                type='closing',
                counter_points=[]
            )
            
            self.arguments_made.append(argument)
            
            return {
                'content': str(response),
                'metadata': {
                    'key_points': debate_analysis.get('key_points', []),
                    'style': self.style.value,
                    'confidence': self._calculate_confidence(argument)
                }
            }
        except Exception as e:
            print(f"Error in generate_closing_statement: {str(e)}")  # Debug print
            return {
                'content': f"Error generating closing statement: {str(e)}",
                'metadata': {
                    'key_points': [],
                    'style': self.style.value,
                    'confidence': 0.0
                }
            }

    def _generate_completion(self, partial_response: str, topic: str) -> str:
        """Generate completion for truncated response"""
        try:
            completion_prompt = f"""Complete this debate statement naturally:
            
            Partial statement: {partial_response}
            Topic: {topic}
            
            Requirements:
            - Continue the thought naturally
            - Maintain the same style and tone
            - End with a complete sentence
            - Maximum 2-3 sentences
            - Must provide proper closure
            """
            
            completion = self.llm(completion_prompt)
            return completion if completion else "."
        except Exception as e:
            print(f"Error in _generate_completion: {str(e)}")  # Debug print
            return "."  # Fallback to simple period if completion fails

    def _calculate_confidence(self, argument: Argument) -> float:
        """Calculate confidence in an argument"""
        base_confidence = argument.strength
        
        # Adjust for personality
        base_confidence *= (1 + self.personality.get('confidence', 0.5) - 0.5)
        
        # Adjust for evidence strength
        evidence_factor = len(argument.evidence) * 0.1
        base_confidence *= (1 + evidence_factor)
        
        return min(base_confidence, 1.0)

    def _evaluate_argument_strength(self, argument: str) -> float:
        """Evaluate the strength of an argument"""
        # Base strength
        strength = 0.7
        
        # Adjust for evidence
        if 'research shows' in argument.lower() or 'studies indicate' in argument.lower():
            strength += 0.1
            
        # Adjust for logical structure
        if 'therefore' in argument.lower() or 'consequently' in argument.lower():
            strength += 0.1
            
        # Adjust for counter-argument addressing
        if 'however' in argument.lower() or 'although' in argument.lower():
            strength += 0.1
            
        return min(strength, 1.0)

    def _extract_claims(self, text: str) -> List[str]:
        """Extract claims from text"""
        if not text or not isinstance(text, str):
            return []
            
        try:
            claims = []
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['claim', 'argues', 'states', 'suggests']):
                    claims.append(sentence.strip())
            return claims if claims else [text.strip()]
        except Exception:
            return []

    def _extract_evidence(self, text: str) -> List[str]:
        """Extract evidence from text"""
        if not text or not isinstance(text, str):
            return []
            
        try:
            evidence = []
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in 
                      ['research', 'study', 'evidence', 'data', 'shows', 'demonstrates']):
                    evidence.append(sentence.strip())
            return evidence
        except Exception:
            return []

    def _extract_weaknesses(self, text: str) -> List[str]:
        """Extract logical weaknesses from text"""
        if not text or not isinstance(text, str):
            return []
            
        try:
            weaknesses = []
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in 
                      ['weakness', 'flaw', 'problem', 'issue', 'lacks', 'fails']):
                    weaknesses.append(sentence.strip())
            return weaknesses
        except Exception:
            return []

    def _extract_counter_points(self, text: str) -> List[str]:
        """Extract counter points from text"""
        if not text or not isinstance(text, str):
            return []
            
        try:
            counter_points = []
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in 
                      ['however', 'but', 'contrary', 'oppose', 'challenge']):
                    counter_points.append(sentence.strip())
            return counter_points
        except Exception:
            return []

    def _generate_counter_points(self, analysis: Dict) -> List[str]:
        """Generate counter points based on analysis"""
        counter_points = []
        
        # Add counter points for each main claim
        for claim in analysis.get('main_claims', []):
            counter_points.append(f"Counter to claim: {claim}")
            
        # Add counter points for weak evidence
        for evidence in analysis.get('evidence', []):
            counter_points.append(f"Challenge evidence: {evidence}")
            
        # Add points targeting weaknesses
        for weakness in analysis.get('weaknesses', []):
            counter_points.append(f"Exploit weakness: {weakness}")
            
        return counter_points[:3]  # Limit to top 3 counter points

    def _analyze_debate_history(self) -> Dict:
        """Analyze the debate history for closing statement"""
        try:
            # Collect all arguments made
            all_arguments = [arg.content for arg in self.arguments_made]
            
            # Extract key points
            key_points = []
            for arg in all_arguments:
                claims = self._extract_claims(arg)
                key_points.extend(claims)
            
            # Get unique key points
            key_points = list(set(key_points))[:5]  # Limit to top 5 points
            
            return {
                'key_points': key_points,
                'total_arguments': len(all_arguments),
                'stance_consistency': self._evaluate_stance_consistency(all_arguments)
            }
        except Exception:
            return {
                'key_points': [],
                'total_arguments': 0,
                'stance_consistency': 1.0
            }

    def _evaluate_stance_consistency(self, arguments: List[str]) -> float:
        """Evaluate how consistently the agent maintained their stance"""
        try:
            consistency_score = 1.0
            stance_indicators = {
                'in favor': ['support', 'agree', 'advocate', 'beneficial', 'positive'],
                'against': ['oppose', 'disagree', 'harmful', 'negative', 'against']
            }
            
            expected_indicators = stance_indicators[self.stance]
            
            for arg in arguments:
                # Check if argument contains opposite stance indicators
                if any(word in arg.lower() for word in stance_indicators['in favor' if self.stance == 'against' else 'against']):
                    consistency_score -= 0.1
                    
            return max(consistency_score, 0.0)
        except Exception:
            return 1.0

    def learn(self, feedback: Dict):
        """Learn from debate feedback"""
        super().learn(feedback)
        
        # Update debate-specific traits
        if feedback.get('argument_effective', False):
            self.personality['persuasiveness'] = min(
                self.personality['persuasiveness'] + 0.05,
                1.0
            )
        
        # Learn from opponent's arguments
        for arg in feedback.get('successful_opponent_arguments', []):
            self._analyze_and_learn_from_argument(arg)

    def _analyze_and_learn_from_argument(self, argument: str):
        """Analyze and learn from successful opponent arguments"""
        analysis = self._analyze_opponent_argument(argument)
        
        # Store effective counter-arguments
        if analysis.get('counter_points'):
            self.store_memory(Memory(
                content=str(analysis['counter_points']),
                importance=0.8,
                context={'type': 'effective_argument'},
                timestamp=time.time(),
                type='semantic'
            ))