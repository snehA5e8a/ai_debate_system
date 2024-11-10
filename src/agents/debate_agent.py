from typing import Dict
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
        
    def analyze_opponent(self, argument: str) -> Dict:
        """Analyze opponent's argument to target counter-arguments by 
        Extracting specific claims to counter
        Identifing  evidence gaps to exploit"""
        try:
            analysis_prompt = f"""Extract from this argument:{argument} under 100 words
    

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
            
            Present a compelling opening argument supporting your position on {topic} under 140 words 
            Requirements:
            - Begin with a clear position statement
            - Support each argument with specific evidence
            - Use natural transitions between ideas without mentioning position, argument 1, 2 etc
            - Maintain {parameters['debate_style'].lower()} tone
            - End with a strong concluding sentence

            Do not:
            - Exceed 140 words
            - Include instructions or explanations
            - Use bullet points or numbered lists
            - Make meta-references 
            - Start with "I believe" or "Explanation" or "Example:" similar phrases 

            
            Start directly with your first argument. Connect your points with smooth transitions. End with a clear conclusion that ties your arguments together.
            

        """

        try:
            response1 = self.llm(prompt)
            response = self.clean_response(response1)
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
        
        prompt = f""" On Topic: {topic} you are taking {self.stance} stance

    Create an argument that opposes the opponent's argument: {opponent_argument}
    Based on opponent's argument: {analysis.get('analysis', '')}
    While creating this argument,keep in mind your Previous discussion points: {previous_points} to
    1. Address opponent's key points directly
    2. Build upon rather than just oppose
    3. Advance the discussion with new insights
    4. Connect arguments to broader implications
    5. Present new supporting evidence
    6. Use {parameters['debate_style'].lower()} tone

    Do not:
    - Cycle back to previous arguments
    - Simply negate opponent's points
    - Use meta-debate language
    - List points with markers
    
    Begin the response directly with your counterargument."""

        try:
            response1 = self.llm(prompt)
            response = self.clean_response(response1)
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
            response = self.clean_response(response1)
            if not response or response.isspace():
                response = f"Error: Could not generate closing statement for {self.stance} position"
            self.remember(response, "closing")
            return response
        except Exception as e:
            return f"Error generating closing statement for {self.stance} position"
        
