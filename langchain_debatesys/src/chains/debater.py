from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.callbacks import CallbackManager
from typing import Dict, List, Optional
import time
from .config import DebateStyle, DEBATE_PROMPTS

class ArgumentAnalyzer(LLMChain):
    """Chain for analyzing opponent arguments"""
    
    def __init__(self, llm):
        prompt = PromptTemplate(
            input_variables=["argument"],
            template="""Analyze this debate argument and extract:
            1. Main claims made
            2. Evidence provided
            3. Logical weaknesses
            4. Potential counter-arguments

            Argument: {argument}
            
            Format your response as:
            Claims: (list main claims)
            Evidence: (list evidence)
            Weaknesses: (list weaknesses)
            Counter-points: (list counter-arguments)"""
        )
        super().__init__(llm=llm, prompt=prompt)
    
    def analyze(self, argument: str) -> Dict:
        """Analyze an argument and return structured results"""
        try:
            result = self({"argument": argument})
            analysis = self._parse_analysis(result["text"])
            return analysis
        except Exception:
            return {
                "claims": [],
                "evidence": [],
                "weaknesses": [],
                "counter_points": []
            }
    
    def _parse_analysis(self, text: str) -> Dict:
        """Parse the analysis response into structured format"""
        sections = {
            "claims": [],
            "evidence": [],
            "weaknesses": [],
            "counter_points": []
        }
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            for section in sections:
                if line.lower().startswith(f"{section}:"):
                    current_section = section
                    break
            
            if current_section and not line.endswith(':'):
                sections[current_section].append(line)
        
        return sections

class DebateChain(LLMChain):
    """Chain for generating debate arguments"""
    
    def __init__(self, llm, name: str, stance: str, style: DebateStyle, memory=None):
        self.name = name
        self.stance = stance
        self.style = style
        self.analyzer = ArgumentAnalyzer(llm)
        self.arguments_made = []
        
        # Initialize metrics
        self.metrics = {
            "arguments_made": 0,
            "evidence_used": 0,
            "counter_points_addressed": 0
        }
        
        super().__init__(
            llm=llm,
            prompt=DEBATE_PROMPTS["opening"],
            memory=memory,
            verbose=True
        )
    
    def generate_opening(self, topic: str) -> Dict:
        """Generate opening statement"""
        try:
            response = self({
                "topic": topic,
                "stance": self.stance,
                "style": self.style.value
            })
            
            self.arguments_made.append({
                "type": "opening",
                "content": response["text"],
                "timestamp": time.time()
            })
            
            self.metrics["arguments_made"] += 1
            
            return {
                "content": response["text"],
                "metadata": {
                    "stance": self.stance,
                    "style": self.style.value,
                    "confidence": self._calculate_confidence(response["text"])
                }
            }
        except Exception as e:
            return {
                "content": f"Error generating opening: {str(e)}",
                "metadata": {"error": True}
            }
    
    def generate_rebuttal(self, topic: str, previous_argument: str) -> Dict:
        """Generate rebuttal to opponent's argument"""
        try:
            # Analyze opponent's argument
            analysis = self.analyzer.analyze(previous_argument)
            
            # Update prompt for rebuttal
            self.prompt = DEBATE_PROMPTS["rebuttal"]
            
            response = self({
                "topic": topic,
                "stance": self.stance,
                "style": self.style.value,
                "previous_argument": previous_argument
            })
            
            self.arguments_made.append({
                "type": "rebuttal",
                "content": response["text"],
                "analysis": analysis,
                "timestamp": time.time()
            })
            
            self.metrics["arguments_made"] += 1
            self.metrics["counter_points_addressed"] += len(analysis["counter_points"])
            
            return {
                "content": response["text"],
                "metadata": {
                    "points_addressed": analysis["counter_points"],
                    "style": self.style.value,
                    "confidence": self._calculate_confidence(response["text"])
                }
            }
        except Exception as e:
            return {
                "content": f"Error generating rebuttal: {str(e)}",
                "metadata": {"error": True}
            }
    
    def generate_closing(self, topic: str) -> Dict:
        """Generate closing statement"""
        try:
            # Prepare debate history
            debate_history = "\n".join(
                f"- {arg['content']}" for arg in self.arguments_made
            )
            
            self.prompt = DEBATE_PROMPTS["closing"]
            
            response = self({
                "topic": topic,
                "stance": self.stance,
                "style": self.style.value,
                "debate_history": debate_history
            })
            
            self.arguments_made.append({
                "type": "closing",
                "content": response["text"],
                "timestamp": time.time()
            })
            
            self.metrics["arguments_made"] += 1
            
            return {
                "content": response["text"],
                "metadata": {
                    "metrics": self.metrics,
                    "style": self.style.value,
                    "confidence": self._calculate_confidence(response["text"])
                }
            }
        except Exception as e:
            return {
                "content": f"Error generating closing: {str(e)}",
                "metadata": {"error": True}
            }
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for an argument"""
        base_confidence = 0.7
        
        # Adjust for evidence
        evidence_terms = ['research shows', 'studies indicate', 'evidence suggests']
        if any(term in text.lower() for term in evidence_terms):
            base_confidence += 0.1
            self.metrics["evidence_used"] += 1
        
        # Adjust for logical structure
        logic_terms = ['therefore', 'consequently', 'thus', 'hence']
        if any(term in text.lower() for term in logic_terms):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)