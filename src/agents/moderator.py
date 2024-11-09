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
    def __init__(self, llm, debate_log = []):
        self.llm = llm
        self.debate_history = []
    
    def moderate(self, topic: str, stage: str) -> str:
        """Provides moderation text for debate stages"""
        stage_prompts = {
            "introduction": f"""You are the moderator of a debate on topic: {topic}. Give an introduction to the debate by 
                - Start by Welcoming the audience and introducing yourself.
                - Clearly state the topic of the debate.
                - Provide a brief overview of why this topic is important or relevant.
                - Pass the floor to the debaters for their opening statements, starting with [Debater 1's Name].
                Do not:
                - No sentences before welcoming statement 
                - Include examples or templates
                - Add instructions about moderation
                - Use meta-language about debates
                - Mention debate rules or expectations
                - Use phrases like "join us" or "example:
                - Exceed 3 sentences
                - Do not include "in length Here's a good example for you:"
                """,

            "transition": f"""Moderating our discussion on {topic} after hearing one argument each from opponent and proponent.
                The debate history so far: {self.debate_history}
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