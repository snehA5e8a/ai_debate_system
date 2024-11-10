import time
from typing import Dict
from .utils import clean_response


class FactCheckerAgent:
    """
    Fact checker with agentic properties:
    - Goals: Ensure factual accuracy
    - Actions: Verify claims and provide ratings
    - Perception: Monitor statements
    - Memory: Track verified facts
    - Learning: Improve verification accuracy
    """
    def __init__(self, llm):
        self.llm = llm
        self.verified_facts = {}
        self.verification_history = []
    
    
    def check_facts(self, statement: str) -> str:
        """Improved fact checking with focused output"""
        prompt = f"""Analyze for factual accuracy (2-3 claims only):
        {statement}
        
        Format strictly as follows: 
        CLAIM: [exact claim]\n
        RATING: [Verified/Unverified/Misleading] \n
        REASON: [one specific reason] 
        
        Maximum 3 claims. Focus on numerical/statistical claims.

        No additional text or explanations."""
        
        try:
            result1 = self.llm(prompt)
            result = clean_response(result1)
            self.verified_facts[statement] = result
            self.verification_history.append({
                "statement": statement,
                "result": result,
                "timestamp": time.time()
            })
            return result
        except Exception as e:
            return f"Fact check error: {str(e)}"
