import time
from typing import Dict

class ModeratorAgent:
    """
    Moderator with agentic properties:
    - Goals: Facilitate fair debate
    - Actions: Guide discussion, maintain order
    - Perception: Monitor debate flow
    - Memory: Track debate progress
    - Learning: Adapt moderation style
    """
    def __init__(self, llm):
        self.llm = llm
        self.debate_history = []
    
    def moderate(self, topic: str, stage: str) -> str:
        """Provides moderation text for debate stages"""
        stage_prompts = {
            "introduction": f"""As a moderator, introduce this discussion on: {topic}

Provide a brief, neutral introduction that:
- Clearly states the topic
- Sets expectations for constructive dialogue
- Encourages evidence-based discussion

Keep it concise and focused.""",

            "transition": f"""Guide the discussion on {topic} to the next phase.

Provide a brief transition that:
- Acknowledges points made
- Maintains discussion flow
- Ensures balanced participation

Be concise and neutral.""",

            "closing": f"""Conclude the discussion on: {topic}

Provide a brief closing that:
- Acknowledges key points discussed
- Maintains neutrality
- Emphasizes the value of the discussion

Keep it concise and constructive."""
        }
        
        try:
            response = self.llm(stage_prompts.get(stage, stage_prompts["transition"]))
            self.debate_history.append({
                "stage": stage,
                "content": response,
                "timestamp": time.time()
            })
            return response
        except Exception as e:
            return f"Moderation error: {str(e)}"