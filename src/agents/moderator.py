from typing import Dict, List, Optional
import time
from .base_agent import BaseAgent, AgentState, AgentEmotion, Memory, Goal

class ModeratorAgent(BaseAgent):
    """Specialized agent for debate moderation"""
    def __init__(self, llm):
        super().__init__(name="Moderator", role="moderator", llm=llm)
        self.debate_state = {
            'topic': None,
            'current_stage': 'not_started',
            'speaker_order': ['Proponent', 'Opponent'],
            'time_tracking': {},
            'interventions_made': [],
            'speaker_times': {'Proponent': 0, 'Opponent': 0},
            'last_speaker_start': None,
            'inappropriate_content_count': 0,
            'interruptions': 0,
            'topic_adherence_score': 1.0
        }
        
        # Time limits in seconds
        self.time_limits = {
            'opening': 180,    # 3 minutes
            'rebuttal': 120,   # 2 minutes
            'closing': 180     # 3 minutes
        }
        
        # Initialize moderator-specific goals
        self.goals.append(Goal(
            description="Ensure fair debate",
            priority=1.0,
            progress=0.0
        ))
        self.goals.append(Goal(
            description="Maintain productive discussion",
            priority=0.9,
            progress=0.0
        ))

    def moderate(self, topic: str, stage: str) -> Dict:
        """Provide moderation for debate stage"""
        self.debate_state['topic'] = topic
        self.debate_state['current_stage'] = stage
        
        try:
            if stage == "introduction":
                return self._generate_introduction(topic)
            elif stage == "transition":
                return self._generate_transition()
            elif stage == "intervention":
                return self._generate_intervention()
            elif stage == "closing":
                return self._generate_closing()
            else:
                return {
                    'content': f"Unknown stage: {stage}",
                    'metadata': {
                        'stage': stage,
                        'error': True
                    }
                }
        except Exception as e:
            return {
                'content': f"Moderation error: {str(e)}",
                'metadata': {
                    'stage': stage,
                    'error': True
                }
            }

    def _generate_introduction(self, topic: str) -> Dict:
        """Generate debate introduction"""
        prompt = f"""Generate a debate introduction for the topic: {topic}
        
        Requirements:
        - Welcome audience
        - Introduce topic
        - Explain topic's importance
        - Set expectations for debate
        - Maintain neutral tone
        - No meta-text or explanations
        Maximum 130 words.
        """
        
        try:
            response = self.llm(prompt)
            
            # Store in debate state
            self.debate_state['time_tracking']['start_time'] = time.time()
            
            return {
                'content': str(response),
                'metadata': {
                    'stage': 'introduction',
                    'topic': topic,
                    'timestamp': time.time()
                }
            }
        except Exception as e:
            return {
                'content': f"Error generating introduction: {str(e)}",
                'metadata': {
                    'stage': 'introduction',
                    'error': True
                }
            }

    def _generate_transition(self) -> Dict:
        """Generate transition between debate segments"""
        last_speaker = self.debate_state.get('last_speaker', '')
        next_speaker = self._determine_next_speaker()
        
        prompt = f"""Generate a transition statement:
        Last Speaker: {last_speaker}
        Next Speaker: {next_speaker}
        Topic: {self.debate_state['topic']}
        
        Requirements:
        - Brief acknowledgment of previous speaker
        - Clear handoff to next speaker
        - Maintain flow of debate
        - Neutral tone
        Maximum 50 words.
        """
        
        try:
            response = self.llm(prompt)
            
            # Update debate state
            self.debate_state['last_speaker'] = next_speaker
            self.debate_state['last_speaker_start'] = time.time()
            
            return {
                'content': str(response),
                'metadata': {
                    'stage': 'transition',
                    'next_speaker': next_speaker,
                    'timestamp': time.time()
                }
            }
        except Exception as e:
            return {
                'content': f"Error generating transition: {str(e)}",
                'metadata': {
                    'stage': 'transition',
                    'error': True
                }
            }

    def _generate_intervention(self) -> Dict:
        """Generate intervention when needed"""
        intervention_reason = self._check_intervention_needed()
        
        if not intervention_reason:
            return {
                'content': '',
                'metadata': {
                    'stage': 'intervention',
                    'intervention_needed': False
                }
            }
            
        prompt = f"""Generate an intervention statement:
        Reason: {intervention_reason}
        Topic: {self.debate_state['topic']}
        
        Requirements:
        - Diplomatic but firm tone
        - Clear explanation of issue
        - Specific guidance for correction
        - Maintain neutral stance
        Maximum 75 words.
        """
        
        try:
            response = self.llm(prompt)
            
            # Record intervention
            self.debate_state['interventions_made'].append({
                'reason': intervention_reason,
                'timestamp': time.time(),
                'content': str(response)
            })
            
            return {
                'content': str(response),
                'metadata': {
                    'stage': 'intervention',
                    'reason': intervention_reason,
                    'timestamp': time.time()
                }
            }
        except Exception as e:
            return {
                'content': f"Error generating intervention: {str(e)}",
                'metadata': {
                    'stage': 'intervention',
                    'error': True
                }
            }

    def _generate_closing(self) -> Dict:
        """Generate debate closing"""
        debate_summary = self._summarize_debate()
        
        prompt = f"""Generate a debate closing statement:
        Topic: {self.debate_state['topic']}
        Key Points: {debate_summary['key_points']}
        
        Requirements:
        - Thank participants
        - Summarize key points discussed
        - Neutral closing remarks
        - No personal opinions
        - No meta-text or explanations
        Maximum 100 words.
        """
        
        try:
            response = self.llm(prompt)
            
            # Update debate state
            self.debate_state['time_tracking']['end_time'] = time.time()
            
            return {
                'content': str(response),
                'metadata': {
                    'stage': 'closing',
                    'duration': self._calculate_debate_duration(),
                    'summary': debate_summary,
                    'timestamp': time.time()
                }
            }
        except Exception as e:
            return {
                'content': f"Error generating closing: {str(e)}",
                'metadata': {
                    'stage': 'closing',
                    'error': True
                }
            }

    def _check_intervention_needed(self) -> Optional[str]:
        """Check if moderator intervention is needed"""
        # Check for various intervention triggers
        if self._check_time_violation():
            return "Time limit exceeded"
        if self._check_off_topic():
            return "Discussion off topic"
        if self._check_inappropriate_content():
            return "Inappropriate content"
        if self._check_interruption():
            return "Speaker interruption"
        return None

    def _check_time_violation(self) -> bool:
        """Check if current speaker has exceeded time limit"""
        if not self.debate_state['last_speaker_start']:
            return False
            
        current_time = time.time()
        speaking_time = current_time - self.debate_state['last_speaker_start']
        stage = self.debate_state['current_stage']
        
        return speaking_time > self.time_limits.get(stage, 120)

    def _check_off_topic(self) -> bool:
        """Check if discussion has gone off topic"""
        return self.debate_state['topic_adherence_score'] < 0.5

    def _check_inappropriate_content(self) -> bool:
        """Check for inappropriate content"""
        return self.debate_state['inappropriate_content_count'] > 0

    def _check_interruption(self) -> bool:
        """Check for speaker interruptions"""
        return self.debate_state['interruptions'] > 0

    def _determine_next_speaker(self) -> str:
        """Determine who should speak next"""
        current_speaker = self.debate_state.get('last_speaker', '')
        speaker_order = self.debate_state['speaker_order']
        
        if not current_speaker:
            return speaker_order[0]
        
        current_index = speaker_order.index(current_speaker)
        next_index = (current_index + 1) % len(speaker_order)
        return speaker_order[next_index]

    def _calculate_debate_duration(self) -> float:
        """Calculate total debate duration"""
        start_time = self.debate_state['time_tracking'].get('start_time', 0)
        end_time = self.debate_state['time_tracking'].get('end_time', time.time())
        return end_time - start_time

    def _summarize_debate(self) -> Dict:
        """Generate debate summary"""
        all_content = []
        for memory in self.memories:
            if memory.type == 'debate_content':
                all_content.append(memory.content)
                
        prompt = f"""Summarize the key points from this debate:
        Content: {' '.join(all_content)}
        
        Extract:
        1. Main arguments presented
        2. Key evidence provided
        3. Major points of disagreement
        4. Areas of consensus
        """
        
        try:
            response = self.llm(prompt)
            return self._parse_summary(response)
        except Exception:
            return {
                'key_points': [],
                'evidence': [],
                'disagreements': [],
                'consensus': []
            }

    def _parse_summary(self, response: str) -> Dict:
        """Parse the summary response into structured format"""
        try:
            lines = response.split('\n')
            summary = {
                'key_points': [],
                'evidence': [],
                'disagreements': [],
                'consensus': []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if 'main arguments' in line.lower():
                    current_section = 'key_points'
                elif 'evidence' in line.lower():
                    current_section = 'evidence'
                elif 'disagreement' in line.lower():
                    current_section = 'disagreements'
                elif 'consensus' in line.lower():
                    current_section = 'consensus'
                elif line and current_section:
                    summary[current_section].append(line)
                    
            return summary
        except Exception:
            return {
                'key_points': [],
                'evidence': [],
                'disagreements': [],
                'consensus': []
            }

    def get_debate_analytics(self) -> Dict:
        """Get analytics about the debate"""
        return {
            'duration': self._calculate_debate_duration(),
            'interventions': len(self.debate_state['interventions_made']),
            'speaker_balance': self._calculate_speaker_balance(),
            'topic_adherence': self.debate_state['topic_adherence_score'],
            'debate_flow': self._analyze_debate_flow()
        }

    def _calculate_speaker_balance(self) -> float:
        """Calculate how balanced the speaking time was"""
        total_time = sum(self.debate_state['speaker_times'].values())
        if total_time == 0:
            return 1.0
            
        times = list(self.debate_state['speaker_times'].values())
        if len(times) < 2:
            return 1.0
            
        # Calculate deviation from perfect balance
        perfect_share = 1.0 / len(times)
        actual_shares = [t/total_time for t in times]
        max_deviation = max(abs(share - perfect_share) for share in actual_shares)
        
        # Convert to a 0-1 score where 1 is perfect balance
        return 1.0 - (max_deviation / perfect_share)

    def _analyze_debate_flow(self) -> Dict:
        """Analyze the flow and quality of debate"""
        return {
            'topic_coverage': self.debate_state['topic_adherence_score'],
            'interruptions': self.debate_state['interruptions'],
            'inappropriate_content': self.debate_state['inappropriate_content_count'],
            'interventions_needed': len(self.debate_state['interventions_made'])
        }

    def update_speaker_time(self, speaker: str, duration: float):
        """Update the speaking time for a participant"""
        if speaker in self.debate_state['speaker_times']:
            self.debate_state['speaker_times'][speaker] += duration

    def record_interruption(self):
        """Record a speaker interruption"""
        self.debate_state['interruptions'] += 1

    def update_topic_adherence(self, score: float):
        """Update the topic adherence score"""
        self.debate_state['topic_adherence_score'] = min(
            1.0, 
            (self.debate_state['topic_adherence_score'] + score) / 2
        )

    def record_inappropriate_content(self):
        """Record occurrence of inappropriate content"""
        self.debate_state['inappropriate_content_count'] += 1