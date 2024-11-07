import time
from typing import Dict

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
        """Verifies facts in a statement"""
        prompt = f"""Analyze this statement for factual accuracy:

{statement}

Respond with only:
1. Extract 2-3 key factual claims from the statement (ignore opinions)
2. For each claim:
   - State the claim directly
   - Rate accuracy: Verified, Unverified, or Misleading
   - Provide ONE brief, specific reason for the rating
3. Keep technical details and statistics focused only on the exact claims made

Do not:
- Include examples or hypotheticals
- Reference studies or reports not directly relevant
- Make predictions or assumptions
- Use phrases like "Example:" or "Analysis:"
- Include caveats or general context
- Quote statistics unless directly checking a number in the statement

Format:

CLAIM: [exact claim from text]
RATING: [Verified/Unverified/Misleading]
REASON: [one specific, direct reason for rating]

[Repeat for each claim]"""
        
        try:
            result = self.llm(prompt)
            self.verified_facts[statement] = result
            self.verification_history.append({
                "statement": statement,
                "result": result,
                "timestamp": time.time()
            })
            return result
        except Exception as e:
            return f"Fact check error: {str(e)}"

