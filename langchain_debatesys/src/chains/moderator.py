from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from typing import Dict, List, Optional
import time

class TimingTool(BaseTool):
    """Tool for managing debate timing"""
    name = "debate_timer"
    description = "Track and manage debate timing"
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.speaker_times = {}
        self.stage_times = {
            'opening': 180,    # 3 minutes
            'rebuttal': 120,   # 2 minutes
            'closing': 180     # 3 minutes
        }
    
    def _run(self, speaker: Optional[str] = None, stage: Optional[str] = None) -> Dict:
        current_time = time.time()
        if not self.start_time:
            self.start_time = current_time
            return {"status": "started"}
            
        if speaker:
            duration = current_time - self.speaker_times.get(speaker, current_time)
            self.speaker_times[speaker] = current_time
            
            # Check for time limit violation
            if stage and duration > self.stage_times.get(stage, 120):
                return {
                    "status": "time_violation",
                    "speaker": speaker,
                    "duration": duration,
                    "limit": self.stage_times.get(stage, 120)
                }
            
            return {
                "status": "speaking",
                "speaker": speaker,
                "duration": duration,
                "total_time": current_time - self.start_time
            }
            
        return {
            "status": "ongoing",
            "total_time": current_time - self.start_time
        }

class TopicAdherenceTool(BaseTool):
    """Tool for monitoring topic adherence"""
    name = "topic_monitor"
    description = "Monitor debate topic adherence"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
        self.topic_scores = []
        
    def _run(self, content: str, topic: str) -> Dict:
        prompt = f"""Rate how well this content stays on topic.
        Topic: {topic}
        Content: {content}
        
        Rate from 0-1 where:
        1.0 = Completely on topic
        0.0 = Completely off topic
        
        Return only the numeric score."""
        
        try:
            score = float(self.llm(prompt))
            self.topic_scores.append(score)
            
            return {
                "score": score,
                "average": sum(self.topic_scores) / len(self.topic_scores),
                "needs_intervention": score < 0.5
            }
        except:
            return {"score": 1.0, "needs_intervention": False}

class ContentModerationTool(BaseTool):
    """Tool for content moderation"""
    name = "content_moderator"
    description = "Monitor content appropriateness"
    
    def __init__(self):
        super().__init__()
        self.violation_count = 0
        self.inappropriate_terms = [
            "violent", "abusive", "hate", "discriminatory",
            "threatening", "explicit", "offensive"
        ]
    
    def _run(self, content: str) -> Dict:
        content_lower = content.lower()
        violations = [
            term for term in self.inappropriate_terms 
            if term in content_lower
        ]
        
        if violations:
            self.violation_count += 1
            return {
                "status": "inappropriate",
                "violations": violations,
                "count": self.violation_count,
                "needs_intervention": True
            }
        
        return {
            "status": "appropriate",
            "violations": [],
            "count": self.violation_count,
            "needs_intervention": False
        }

class ModeratorChain(LLMChain):
    """Chain for debate moderation"""
    
    def __init__(self, llm, memory=None):
        self.timer = TimingTool()
        self.topic_monitor = TopicAdherenceTool(llm)
        self.content_moderator = ContentModerationTool()
        
        self.debate_state = {
            'current_stage': 'not_started',
            'speaker_order': ['Proponent', 'Opponent'],
            'last_speaker': None,
            'interventions': [],
            'topic_adherence': 1.0
        }
        
        # Initialize prompt templates
        self.prompts = {
            "introduction": PromptTemplate(
                input_variables=["topic"],
                template="""Moderate a debate on the topic: {topic}
                
                Provide a brief, engaging introduction that:
                1. Welcomes the audience
                2. Introduces the topic and its importance
                3. Sets expectations for a constructive debate
                4. Explains the basic rules and format
                
                Keep it under 130 words and maintain a neutral, professional tone."""
            ),
            
            "intervention": PromptTemplate(
                input_variables=["topic", "reason", "violation_type"],
                template="""As debate moderator, intervention needed:
                Topic: {topic}
                Reason: {reason}
                Violation Type: {violation_type}
                
                Provide a brief, diplomatic intervention that:
                1. Addresses the specific issue
                2. Maintains debate decorum
                3. Guides participants back on track
                
                Keep it under 50 words and be firm but respectful."""
            ),
            
            "transition": PromptTemplate(
                input_variables=["topic", "next_speaker", "stage"],
                template="""Provide a transition to the next speaker.
                Topic: {topic}
                Next Speaker: {next_speaker}
                Stage: {stage}
                
                Create a brief transition that maintains debate flow.
                Keep it under 30 words and remain neutral."""
            ),
            
            "closing": PromptTemplate(
                input_variables=["topic", "duration", "key_points"],
                template="""Provide a closing statement for the debate on: {topic}
                Duration: {duration} minutes
                Key Points Discussed:
                {key_points}
                
                Create a closing that:
                1. Thanks all participants
                2. Summarizes key points objectively
                3. Concludes the session professionally
                
                Keep it under 100 words and maintain neutrality."""
            )
        }
        
        super().__init__(
            llm=llm,
            prompt=self.prompts["introduction"],
            memory=memory,
            verbose=True
        )
    
    def moderate(self, stage: str, **kwargs) -> Dict:
        """Generate moderation content for different debate stages"""
        self.debate_state['current_stage'] = stage
        
        try:
            # Update timing
            timing_result = self.timer._run(
                kwargs.get('speaker'),
                stage
            )
            
            # Check for intervention needs
            intervention_needed = self._check_intervention_needed(kwargs)
            if intervention_needed:
                return self._handle_intervention(intervention_needed, kwargs)
            
            # Handle different stages
            if stage == "introduction":
                return self._handle_introduction(kwargs)
            elif stage == "transition":
                return self._handle_transition(kwargs)
            elif stage == "closing":
                return self._handle_closing(kwargs)
            else:
                return {"content": f"Unknown stage: {stage}"}
                
        except Exception as e:
            return {
                "content": f"Moderation error: {str(e)}",
                "metadata": {"stage": stage, "error": True}
            }
    
    def _check_intervention_needed(self, kwargs: Dict) -> Optional[Dict]:
        """Check if moderator intervention is needed"""
        if 'content' not in kwargs:
            return None
            
        # Check time violations
        timing = self.timer._run(kwargs.get('speaker'), kwargs.get('stage'))
        if timing.get('status') == 'time_violation':
            return {
                "reason": "Time limit exceeded",
                "violation_type": "timing",
                "details": timing
            }
        
        # Check topic adherence
        topic_check = self.topic_monitor._run(
            kwargs['content'],
            kwargs.get('topic', '')
        )
        if topic_check.get('needs_intervention'):
            return {
                "reason": "Discussion off topic",
                "violation_type": "topic",
                "details": topic_check
            }
        
        # Check content appropriateness
        content_check = self.content_moderator._run(kwargs['content'])
        if content_check.get('needs_intervention'):
            return {
                "reason": "Inappropriate content",
                "violation_type": "content",
                "details": content_check
            }
        
        return None
    
    def _handle_intervention(self, intervention: Dict, kwargs: Dict) -> Dict:
        """Handle intervention generation"""
        self.prompt = self.prompts["intervention"]
        self.debate_state['interventions'].append({
            'reason': intervention['reason'],
            'timestamp': time.time()
        })
        
        response = self({
            'topic': kwargs.get('topic', ''),
            'reason': intervention['reason'],
            'violation_type': intervention['violation_type']
        })
        
        return {
            'content': response['text'],
            'metadata': {
                'stage': 'intervention',
                'reason': intervention['reason'],
                'details': intervention['details'],
                'timestamp': time.time()
            }
        }
    
    def _handle_introduction(self, kwargs: Dict) -> Dict:
        """Handle introduction generation"""
        self.prompt = self.prompts["introduction"]
        response = self(kwargs)
        
        self.timer._run()  # Start timing
        
        return {
            'content': response['text'],
            'metadata': {
                'stage': 'introduction',
                'timestamp': time.time()
            }
        }
    
    def _handle_transition(self, kwargs: Dict) -> Dict:
        """Handle transition generation"""
        self.prompt = self.prompts["transition"]
        next_speaker = self._determine_next_speaker()
        
        response = self({
            'topic': kwargs.get('topic', ''),
            'next_speaker': next_speaker,
            'stage': self.debate_state['current_stage']
        })
        
        return {
            'content': response['text'],
            'metadata': {
                'stage': 'transition',
                'next_speaker': next_speaker,
                'timestamp': time.time()
            }
        }
    
    def _handle_closing(self, kwargs: Dict) -> Dict:
        """Handle closing generation"""
        self.prompt = self.prompts["closing"]
        duration = (time.time() - self.timer.start_time) / 60  # Convert to minutes
        
        response = self({
            'topic': kwargs.get('topic', ''),
            'duration': f"{duration:.1f}",
            'key_points': kwargs.get('key_points', 'Various points were discussed.')
        })
        
        return {
            'content': response['text'],
            'metadata': {
                'stage': 'closing',
                'duration': duration,
                'interventions': len(self.debate_state['interventions']),
                'topic_adherence': self.debate_state['topic_adherence'],
                'timestamp': time.time()
            }
        }
    
    def _determine_next_speaker(self) -> str:
        """Determine who should speak next"""
        if not self.debate_state['last_speaker']:
            next_speaker = self.debate_state['speaker_order'][0]
        else:
            current_idx = self.debate_state['speaker_order'].index(
                self.debate_state['last_speaker']
            )
            next_speaker = self.debate_state['speaker_order'][
                (current_idx + 1) % len(self.debate_state['speaker_order'])
            ]
        
        self.debate_state['last_speaker'] = next_speaker
        return next_speaker
    
    def get_debate_analytics(self) -> Dict:
        """Get analytics about the debate"""
        end_time = time.time()
        total_duration = end_time - self.timer.start_time if self.timer.start_time else 0
        
        return {
            'duration': total_duration,
            'interventions': len(self.debate_state['interventions']),
            'topic_adherence': self.debate_state['topic_adherence'],
            'speaker_times': self.timer.speaker_times,
            'violations': self.content_moderator.violation_count
        }