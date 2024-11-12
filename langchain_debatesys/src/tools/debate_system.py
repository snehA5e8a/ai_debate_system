from langchain.chains import SequentialChain
from typing import Dict, List
import time
from .config import DebateConfig, DebateMemory
from .moderator import ModeratorChain
from .debater import DebateChain
from .fact_checker import FactCheckerChain

class DebateSystem:
    """Main system orchestrating the debate"""
    
    def __init__(self, llm, config: DebateConfig):
        self.config = config
        self.memory = DebateMemory()
        
        # Initialize chains
        self.moderator = ModeratorChain(llm, memory=self.memory)
        self.proponent = DebateChain(
            llm, 
            "Proponent", 
            "in favor", 
            config.style, 
            memory=self.memory
        )
        self.opponent = DebateChain(
            llm, 
            "Opponent", 
            "against", 
            config.style, 
            memory=self.memory
        )
        self.fact_checker = FactCheckerChain(llm, memory=self.memory)
        
        self.debate_log = []
    
    def log_event(self, event_type: str, content: str, metadata: Dict = None):
        """Log debate events"""
        self.debate_log.append({
            "type": event_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": time.time()
        })
    
    def run_debate(self, topic: str) -> List[Dict]:
        """Run complete debate"""
        try:
            # Introduction
            intro = self.moderator.moderate("introduction", topic=topic)
            self.log_event("MODERATOR", intro["content"], intro["metadata"])
            
            # Opening statements
            for debater in [self.proponent, self.opponent]:
                statement = debater.generate_opening(topic)
                self.log_event(f"{debater.name.upper()}", statement["content"], statement["metadata"])
                
                if self.config.real_time_fact_check:
                    fact_check = self.fact_checker.check_statement(statement["content"])
                    self.log_event("FACT_CHECK", str(fact_check))
            
            # Main debate rounds
            for _ in range(self.config.debate_rounds):
                for debater, opponent in [
                    (self.proponent, self.opponent),
                    (self.opponent, self.proponent)
                ]:
                # Get last opponent argument
                    opponent_args = [
                        log for log in self.debate_log 
                        if log["type"] == opponent.name.upper()
                    ]
                    last_argument = opponent_args[-1]["content"] if opponent_args else ""
                    
                    # Generate rebuttal
                    rebuttal = debater.generate_rebuttal(topic, last_argument)
                    self.log_event(
                        f"{debater.name.upper()}_REBUTTAL",
                        rebuttal["content"],
                        rebuttal["metadata"]
                    )
                    
                    if self.config.real_time_fact_check:
                        fact_check = self.fact_checker.check_statement(rebuttal["content"])
                        self.log_event("FACT_CHECK", str(fact_check))
                    
                    # Check for moderator intervention
                    intervention = self.moderator.moderate(
                        "intervention",
                        topic=topic,
                        reason="Check intervention needed"
                    )
                    if intervention["content"]:
                        self.log_event("MODERATOR", intervention["content"], intervention["metadata"])
            
            # Closing statements
            for debater in [self.proponent, self.opponent]:
                closing = debater.generate_closing(topic)
                self.log_event(
                    f"{debater.name.upper()}_CLOSING",
                    closing["content"],
                    closing["metadata"]
                )
                
                if self.config.real_time_fact_check:
                    fact_check = self.fact_checker.check_statement(closing["content"])
                    self.log_event("FACT_CHECK", str(fact_check))
            
            # Moderator closing
            debate_duration = time.time() - self.debate_log[0]["timestamp"]
            key_points = self._extract_key_points()
            
            closing = self.moderator.moderate(
                "closing",
                topic=topic,
                duration=debate_duration / 60,  # Convert to minutes
                key_points=key_points
            )
            self.log_event("MODERATOR", closing["content"], closing["metadata"])
            
            return self.debate_log
            
        except Exception as e:
            self.log_event("ERROR", str(e))
            return self.debate_log
    
    def _extract_key_points(self) -> List[str]:
        """Extract key points from debate log"""
        key_points = []
        for event in self.debate_log:
            if event["type"].endswith(("_REBUTTAL", "_CLOSING")):
                # Extract main points from content
                points = event["content"].split('.')
                key_points.extend([p.strip() for p in points if len(p.strip()) > 20])
        
        # Return unique points, limited to top 5
        return list(set(key_points))[:5]
    
    def get_analytics(self) -> Dict:
        """Get debate analytics"""
        return {
            "duration": time.time() - self.debate_log[0]["timestamp"],
            "interventions": len([
                e for e in self.debate_log 
                if e["type"] == "MODERATOR" and "intervention" in str(e["metadata"])
            ]),
            "fact_checks": len([
                e for e in self.debate_log 
                if e["type"] == "FACT_CHECK"
            ]),
            "proponent_metrics": self.proponent.metrics,
            "opponent_metrics": self.opponent.metrics
        }