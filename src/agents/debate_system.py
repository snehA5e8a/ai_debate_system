# MAIN SYSTEM ORCHESTRATING(integrating apps to automate process) THE DEBATE

import streamlit as st  # for error handling in this 
from typing import List, Dict
import time

# Using relative imports since we're inside the agents package(to avoid circular import issue)
from .llm import HFInferenceLLM
from .debate_agent import DebateAgent
from .fact_checker import FactCheckerAgent
from .moderator import ModeratorAgent

class DebateSystem:
    """Main system orchestrating the debate"""
    def __init__(self, topic: str, llm, parameters: Dict):
        self.topic = topic
        self.parameters = parameters  # Defined in main.py
        self.debater_pro = DebateAgent("Proponent", "in favor", llm)
        self.debater_con = DebateAgent("Opponent", "against", llm)
        self.fact_checker = FactCheckerAgent(llm)
        self.moderator = ModeratorAgent(llm)
        self.debate_log = []
        
    def log_event(self, event_type: str, content: str):
        """Records debate events"""
        self.debate_log.append({
            'type': event_type,
            'content': content,
            'timestamp': time.time()
        })
        
    def validate_content(self, content: str) -> bool:
        """Check content for inappropriate material"""
        inappropriate_terms = [
            "violent", "abusive", "hate", "discriminatory",
            "threatening", "explicit", "offensive"
        ]
        return not any(term in content.lower() for term in inappropriate_terms)
    
    def run_debate_round(self) -> List[Dict]:
        """Runs a complete debate round"""
        try:
            # Introduction
            intro = self.moderator.moderate(self.topic, "introduction")
            if self.validate_content(intro):
                self.log_event("MODERATOR", intro)
            
            # Opening statements
            for debater in [self.debater_pro, self.debater_con]:
                st.write(f"Generating opening statement for {debater.name}...")
                statement = debater.generate_opening_statement(
                    self.topic, 
                    self.parameters
                )
                
                if self.validate_content(statement):
                    self.log_event(f"{debater.name.upper()}", statement)
                    
                    if self.parameters['fact_checking']:
                        fact_check = self.fact_checker.check_facts(statement)
                        self.log_event("FACT_CHECK", fact_check)
            
            # Main arguments and rebuttals
            for _ in range(self.parameters['debate_rounds']):
                # Pro rebuttal
                pro_rebuttal = self.debater_pro.generate_rebuttal(
                    self.topic,
                    self.debate_log[-2]['content'],
                    self.parameters
                )
                
                if self.validate_content(pro_rebuttal):
                    self.log_event("PROPONENT_REBUTTAL", pro_rebuttal)
                    
                    if self.parameters['fact_checking']:
                        fact_check = self.fact_checker.check_facts(pro_rebuttal)
                        self.log_event("FACT_CHECK", fact_check)
                
                # Con rebuttal
                con_rebuttal = self.debater_con.generate_rebuttal(
                    self.topic,
                    pro_rebuttal,
                    self.parameters
                )
                
                if self.validate_content(con_rebuttal):
                    self.log_event("OPPONENT_REBUTTAL", con_rebuttal)
                    
                    if self.parameters['fact_checking']:
                        fact_check = self.fact_checker.check_facts(con_rebuttal)
                        self.log_event("FACT_CHECK", fact_check)
            
            # Closing statements
            for debater in [self.debater_pro, self.debater_con]:
                closing = debater.generate_closing_statement(
                    self.topic,
                    self.parameters
                )
                
                if self.validate_content(closing):
                    self.log_event(f"{debater.name.upper()}_CLOSING", closing)
            
            # Moderator closing
            closing = self.moderator.moderate(self.topic, "closing")
            if self.validate_content(closing):
                self.log_event("MODERATOR", closing)
            
            return self.debate_log
            
        except Exception as e:
            st.error(f"Error in debate round: {str(e)}")
            return self.debate_log