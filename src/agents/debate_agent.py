from typing import Dict
import time
from .utils import clean_response

class DebateAgent:
    """
    Represents a debater in the system with agentic properties:
    - Goals: Present compelling arguments for assigned viewpoint
    - Actions: Generate statements, rebuttals, and adapt strategy
    - Perception: Analyze opponent's arguments and debate state
    - Memory: Track argument history and points made
    - Learning: Adapt based on opponent's strategy
    """
    def __init__(self, name: str, stance: str, llm):
        self.name= name
        self.memory = []  # to hold the previous arguments/statements
        self.llm = llm
        self.stance = stance
        self.strategy = "balanced"
        self.stats = {
            "arguments_made": 0,
            "rebuttals_made": 0,
            "points_addressed": 0
        }
        
    def remember(self, content: str, type: str):
        """Store information in agent's memory"""
        self.memory.append({
            "content": content,
            "type": type,  # argument or fact checking or any other type of statement made in the debate
            "timestamp": time.time()
        })
        
    def analyze_opponent(self, argument: str) -> Dict:
        """Analyze opponent's argument to target counter-arguments by 
        Extracting specific claims to counter
        Identifing  evidence gaps to exploit"""
        try:
            analysis_prompt = f"""Analyze this argument: {argument}

            Extract exactly:
            1. Main claim being made
            2. Key evidence or examples used
            3. Potential weaknesses or gaps

            Format as:
            MAIN CLAIM: [single sentence]
            EVIDENCE: [bullet points of specific evidence]
            GAPS: [bullet points of weaknesses]

            Keep total response under 80 words.
            Focus only on concrete points, not rhetoric or style."""
            
            analysis = self.llm(analysis_prompt)
            return {"analysis": analysis, "timestamp": time.time()}
        except Exception as e:
            return {"error": str(e)}
        
    def generate_opening_statement(self, topic: str, parameters: Dict) -> str:
        """Generates an opening statement"""
        style_guide = {
            "Formal": "use precise, professional language and academic tone",
            "Casual": "use conversational language while maintaining respect",
            "Academic": "use scholarly language with references to research"
        }
        
        prompt = f"""Topic: {topic}
            Position: {self.stance}
            
            Present a compelling opening argument supporting your position on {topic} under 140 words 
            Requirements:
            - Maximum 130 words
            - Begin with a clear position statement
            - Support each argument with specific evidence
            - Use natural transitions between ideas without mentioning position, argument 1, 2 etc
            - Maintain {parameters['debate_style'].lower()} tone
            - End with a strong concluding sentence

            Do not:
            - Include instructions or explanations
            - Use bullet points or numbered lists
            - Make meta-references 
            - Start with "I believe" or "Explanation" or "Example:" similar phrases 
        
        STOP writing if you reach 130 words.            
        Start directly with your first argument. Connect your points with smooth transitions. End with a clear conclusion that ties your arguments together.
            

        """

        try:
            response1 = self.llm(prompt)
            response = clean_response(response1)
            if not response or response.isspace():
                response = f"Error: Could not generate opening statement for {self.stance} position"
            self.remember(response, "opening")
            self.stats["arguments_made"] += 1
            return response
        except Exception as e:
            return f"Error generating opening statement for {self.stance} position: {e}"
    # rebuttals targeting other side's points as make it more adversarial

    def generate_rebuttal(self, topic: str, opponent_argument: str, parameters: Dict) -> str:
        """Generates a rebuttal with progressive complexity"""
        analysis = self.analyze_opponent(opponent_argument)
        
        
        # Check memory for repeated points
        previous_points = [m['content'] for m in self.memory]
        
        prompt = f""" Topic: {topic}
    Your stance: {self.stance}
    Opponent's argument: {opponent_argument}
    Generate a specific rebuttal that:
    1. Directly addresses the topic "{topic}"
    2. Responds to these key points from opponent's argument:{analysis.get('analysis', '')}

    Requirements:
    - Stay focused on the exact topic
    - Provide specific counterpoints with evidence
    - Use {parameters['debate_style'].lower()} language
    - Keep response under 130 words
    - Make direct references to the topic and opponent's points
    - Include at least one piece of supporting evidence

    Do not:
    - Make generic statements about debate or discourse
    - Use meta-language about arguments
    - Drift to unrelated topics
    - Use debate terminology (e.g., "counterargument", "in conclusion")
    - Make comparisons to unrelated fields
    - Use filler phrases or abstract concepts

    Start directly with your specific rebuttal to the opponent's points about {topic}."""
        try:
            response1 = self.llm(prompt)
            response = clean_response(response1)
            # prevents empty/whitespace responses
            if not response or response.isspace():
                response = f"Error: Could not generate rebuttal for {self.stance} position"
            # These track debate progress and performance
            self.remember(response, "rebuttal")
            self.stats["rebuttals_made"] += 1
            return response
        except Exception as e:
                # Provides error handling with stance context
            return f"Error generating rebuttal for {self.stance} position"

    def generate_closing_statement(self, topic: str, parameters: Dict) -> str:
        """Generates a closing statement based on debate history"""
        style_guide = {
            "Formal": "use precise language and academic tone",
            "Casual": "use conversational language while maintaining respect",
            "Academic": "use scholarly language with references to research"
        }
        # Get previous arguments from memory
        memory_points = "\n".join([f"- {m['content']}" for m in self.memory])
        
        prompt = f"""You are concluding your perspective {self.stance} on: {topic}

                        Previous points discussed:{memory_points}

                        Provide a strong conclusion supporting your stance on {topic} that: 
:
                        - {style_guide[parameters['debate_style']]}
                        - Synthesizes the main arguments presented
                        - Reinforces your key evidence and examples  
                        - Addresses significant counterpoints raised

                        Important Guidelines:
                        - Summarize your position clearly and directly
                        - Avoid debate competition language or formalities
                        - Don't address judges or audience
                        - Focus on the strength of your arguments and evidence
                        - Maintain a constructive, solution-oriented tone

                        Requirements:
                        - Reinforce your main arguments
                        - Address key counterpoints
                        - End with a compelling final thought
                        - Use {parameters['debate_style'].lower()} tone

                        Constraints:
                        - Maximum 2 paragraphs
                        - No summaries starting with "In conclusion"
                        - No meta-debate language
                        - No templates or outlines
                        - No numbered points or markers

Begin directly with your closing argument."""

                        
        try:
            response1 = self.llm(prompt)
            response = clean_response(response1)
            if not response or response.isspace():
                response = f"Error: Could not generate closing statement for {self.stance} position"
            self.remember(response, "closing")
            return response
        except Exception as e:
            return f"Error generating closing statement for {self.stance} position"
        
