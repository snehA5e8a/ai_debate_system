
from typing import Dict
from .base_agent import BaseAgent
import time

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
            analysis_prompt = f"""Extract from this argument:
{argument}

1. List the 3 strongest factual claims made
2. List any statistics or data cited
3. Identify logical assumptions
4. Note any missing evidence

Format response as clear key-value pairs:
CLAIMS: [numbered list of main claims]
EVIDENCE: [any specific data/stats used]
ASSUMPTIONS: [key unstated assumptions]
GAPS: [missing evidence/logical gaps]

Do not:
- Make meta-comments
- Add analysis labels
- Include rebuttals yet
- Evaluate validity"""
            
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

Present a compelling opening argument supporting your position on {topic}. 
requirements:
- Begin with a clear position statement
- Support each argument with specific evidence
- Use natural transitions between ideas without mentioning position, argument 1, 2 etc
- Maintain {parameters['debate_style'].lower()} tone
- End with a strong concluding sentence
Constraints:
- Maximum 3 paragraphs- No numbered points or markers like "firstly"
- No meta-references to the debate
- No phrases like "I believe" or "In this essay"
- No templates or outlines
Do not:
- Use phrases like "Point 1:" or "For example:"
- Include instructions or explanations
- Use bullet points or numbered lists
- Make meta-references 
- Start with "I believe" or similar phrases, Example: 
- Do not use Position:, Argument 1: 

Start directly with your first argument. Connect your points with smooth transitions. End with a clear conclusion that ties your arguments together.

"""

        try:
            response = self.llm(prompt)
            if not response or response.isspace():
                response = f"Error: Could not generate opening statement for {self.stance} position"
            self.remember(response, "opening")
            self.stats["arguments_made"] += 1
            return response
        except Exception as e:
            return f"Error generating opening statement for {self.stance} position"
    # rebuttals targeting other side's points as make it more adversarial

    def generate_rebuttal(self, topic: str, opponent_argument: str, parameters: Dict) -> str:
        """Generates a rebuttal with progressive complexity"""
        analysis = self.analyze_opponent(opponent_argument)
        
        
        # Check memory for repeated points
        previous_points = [m['content'] for m in self.memory]
        
        prompt = f"""Topic: {topic}
    Your stance: {self.stance}
    Previous discussion points: {previous_points}
    Responding to opponent's argument:{opponent_argument}

    Based on opponent's argument:
    {analysis.get('analysis', '')}

    Requirements:
    1. Avoid repeating previous points
    2. Build upon rather than just oppose
    3. Advance the discussion with new insights
    4. Connect arguments to broader implications
    5. Address opponent's key points directly
    6. Present new supporting evidence
    7. Maintain focus on {parameters['focus_points']} main counterpoints
    8. Use {parameters['debate_style'].lower()} tone

    Constraints:
    - Maximum 2-3 paragraphs
    - No marker words like "firstly" or "moreover"
    - No meta-debate language
    - No templates or outlines

    Do not:
    - Cycle back to previous arguments
    - Simply negate opponent's points
    - Use meta-debate language
    - List points with markers
    
    Begin directly with your counterargument."""

        try:
            response = self.llm(prompt)
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
            response = self.llm(prompt)
            if not response or response.isspace():
                response = f"Error: Could not generate closing statement for {self.stance} position"
            self.remember(response, "closing")
            return response
        except Exception as e:
            return f"Error generating closing statement for {self.stance} position"
        
