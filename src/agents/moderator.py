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

    def clean_response(self, response_text):
        # List of tokens/markers to remove
        tokens_to_remove = [
            '<|assistant|>',
            '<|human|>',
            '```',
            '<|system|>',
            '<|user|>', "Point 1:", "For example:", "Position:", "Argument 1:", "join us", "example:"]
    
        # Remove all tokens
        for token in tokens_to_remove:
            response_text = response_text.replace(token, '')
        # Clean up any extra whitespace
        response_text = response_text.strip()
    
         # Remove any multiple consecutive newlines
        response_text = '\n'.join(line for line in response_text.splitlines() if line.strip())
        def clean_response(self, response_text):
        # List of tokens/markers to remove
            tokens_to_remove = [
            '<|assistant|>',
            '<|human|>',
            '```',
            '<|system|>',
            '<|user|>', "Point 1:", "For example:", "Position:", "Argument 1:", "join us", "example:"]
    
            # Remove all tokens
            for token in tokens_to_remove:
                response_text = response_text.replace(token, '')
            # Clean up any extra whitespace
            response_text = response_text.strip()
        
            # Remove any multiple consecutive newlines
            response_text = '\n'.join(line for line in response_text.splitlines() if line.strip())

        return response_text
    
    
    def moderate(self, topic: str, stage: str) -> str:
        """Provides moderation text for debate stages"""
        stage_prompts = {
            "introduction": f"""You are the moderator of a debate on topic: {topic}. Give an introduction to the debate
                Guidelines
                - Start by Welcoming the audience and introducing yourself.
                - Clearly state the topic of the debate.
                - Provide a brief overview of why this topic is important or relevant in one sentence
                - Pass the floor to the debaters for their opening statements, starting with [Debater 1's Name].
                Do not:
                - Exceed 120 words
                - No sentences before welcoming statement 
                - Include examples or templates
                - Add instructions about moderation
                - Use meta-language about debates
                - Mention debate rules or expectations
                """,

            "transition": f"""Moderating our discussion on {topic} after hearing one argument each from opponent and proponent.
                The debate history so far: {self.debate_history}
                Provide only:
                1. A single acknowledgment of the previous point
                2. A brief direction for the next speaker

                Do not:
                - Exceed 120 words
                - Add examples
                - Include moderation instructions
                """,

            "closing": f"""Concluding our discussion on {topic}.

                    Provide only:
                    1. A single acknowledgment of perspectives shared
                    2. A brief closing statement

                    Do not:
                    - Exceed 120 words
                    - Add examples
                    - Include summaries
                    - Use phrases like "join us" or "example:"


                    Keep the closing to 120 words maximum."""
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