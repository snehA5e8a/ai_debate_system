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
            "introduction": f"""Topic: {topic}

This question has sparked significant debate, with compelling perspectives on both sides. Today we'll explore the key arguments for and against {topic.lower()}.

Present:
1. A clear statement of the topic
2. A concise framing of the core question
3. A single sentence inviting balanced perspectives

Do not:
- Include examples or templates
- Add instructions about moderation
- Use meta-language about debates
- Mention debate rules or expectations
- Use phrases like "join us" or "example:
- Exceed 3 sentences"

Keep the introduction to 2-3 sentences maximum.""",

            "transition": f"""Transitioning our discussion on {topic}.

Provide only:
1. A single acknowledgment of the previous point
2. A brief direction for the next speaker

Do not:
- Add examples
- Include moderation instructions
- Use phrases like "for example" or "join us"

Keep the transition to 1-2 sentences maximum.""",

            "closing": f"""Concluding our discussion on {topic}.

Provide only:
1. A single acknowledgment of perspectives shared
2. A brief closing statement

Do not:
- Add examples
- Include summaries
- Use phrases like "join us" or "example:"

Keep the closing to 2 sentences maximum."""
        }
        
        try:
            response = self.llm(stage_prompts.get(stage, ""))
            self.debate_history.append({
                "stage": stage,
                "content": response,
                "timestamp": time.time()
            })
            return response
        except Exception as e:
            return f"Moderation error: {str(e)}"