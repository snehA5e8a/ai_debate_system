
from typing import Dict
from .base_agent import BaseAgent

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
        self.llm = llm
        self.stance = stance
        self.strategy = "balanced"
        """self.stats.update({
            "arguments_made": 0,
            "rebuttals_made": 0,
            "points_addressed": 0
        })"""
        
    def analyze_opponent(self, argument: str) -> Dict:
        """Analyze opponent's argument to adapt strategy"""
        try:
            analysis_prompt = f"""Analyze this argument:
            {argument}
            
            Identify:
            1. Main points
            2. Evidence strength
            3. Emotional vs logical balance
            4. Potential weaknesses"""
            
            analysis = self.llm(analysis_prompt)
            return {"analysis": analysis, "timestamp": time.time()}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_opening_statement(self, topic: str, parameters: Dict) -> str:
        """Generates an opening statement"""
        style_guide = {
            "Formal": "use precise language and academic tone",
            "Casual": "use conversational language while maintaining respect",
            "Academic": "use scholarly language with references to research"
        }
        
        prompt = f"""You are presenting a perspective {self.stance} on: {topic}

Present your opening viewpoint that:
- {style_guide[parameters['debate_style']]}
- Makes {parameters['focus_points']} clear points
- Backs claims with specific examples or evidence
- Maintains a {self.strategy} and constructive tone

Important Guidelines:
- Focus on presenting your perspective directly
- Avoid debate competition language or addressing judges
- Don't use phrases like "honorable judges" or "dear audience"
- Present your points naturally as if in an informed discussion
- Stay focused on the topic and evidence

Begin your response with a clear statement of your position."""
        
        try:
            response = self.llm(prompt)
            if not response or response.isspace():
                response = f"Error: Could not generate opening statement for {self.stance} position"
            self.remember(response, "opening")
            #self.stats["arguments_made"] += 1
            return response
        except Exception as e:
            return f"Error generating opening statement for {self.stance} position"
    
    def generate_rebuttal(self, topic: str, opponent_argument: str, parameters: Dict) -> str:
        """Generates a rebuttal to opponent's argument"""
        analysis = self.analyze_opponent(opponent_argument)
        
        style_guide = {
            "Formal": "use precise language and academic tone",
            "Casual": "use conversational language while maintaining respect",
            "Academic": "use scholarly language with references to research"
        }
        
        prompt = f"""You are continuing a discussion {self.stance} on: {topic}

Previous argument to address: {opponent_argument}

Based on analysis: {analysis.get('analysis', 'No analysis available')}

Provide a response that:
- {style_guide[parameters['debate_style']]}
- Addresses {parameters['focus_points']} key points from the previous argument
- Presents counter-evidence or alternative perspectives
- Maintains a {self.strategy} and constructive approach

Important Guidelines:
- Address the arguments directly without debate formalities
- Focus on the substance of the counter-arguments
- Avoid competitive debate language or addressing judges
- Present your points as part of a reasoned discussion
- Keep responses evidence-based and logical

Start by directly addressing the most significant point raised."""
        
        try:
            response = self.llm(prompt)
            if not response or response.isspace():
                response = f"Error: Could not generate rebuttal for {self.stance} position"
            self.remember(response, "rebuttal")
            #self.stats["rebuttals_made"] += 1
            return response
        except Exception as e:
            return f"Error generating rebuttal for {self.stance} position"

    def generate_closing_statement(self, topic: str, parameters: Dict) -> str:
        """Generates a closing statement based on debate history"""
        style_guide = {
            "Formal": "use precise language and academic tone",
            "Casual": "use conversational language while maintaining respect",
            "Academic": "use scholarly language with references to research"
        }
        
        memory_points = "\n".join([f"- {m['content']}" for m in self.memory])
        
        prompt = f"""You are concluding your perspective {self.stance} on: {topic}

Previous points discussed:
{memory_points}

Provide a conclusion that:
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

Begin with a clear restatement of your main position."""
        
        try:
            response = self.llm(prompt)
            if not response or response.isspace():
                response = f"Error: Could not generate closing statement for {self.stance} position"
            self.remember(response, "closing")
            return response
        except Exception as e:
            return f"Error generating closing statement for {self.stance} position"
        
