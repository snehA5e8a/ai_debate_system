from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel
from enum import Enum
from typing import List, Dict, Optional

class DebateStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    ACADEMIC = "academic"

class DebateConfig(BaseModel):
    debate_rounds: int = 2
    focus_points: int = 3
    show_thinking: bool = True
    real_time_fact_check: bool = True
    style: DebateStyle = DebateStyle.FORMAL
    agent_base_confidence: float = 0.7
    agent_adaptability: float = 0.5

class DebateMemory(ConversationBufferWindowMemory):
    def __init__(self, k: int = 5):
        super().__init__(k=k, return_messages=True, memory_key="chat_history")
        
    def add_agent_message(self, agent_name: str, message: str):
        self.chat_memory.add_user_message(f"{agent_name}: {message}")

# Common prompt templates
DEBATE_PROMPTS = {
    "opening": PromptTemplate(
        input_variables=["topic", "stance", "style"],
        template="""As a {stance} debater in a {style} debate about '{topic}', 
        provide an opening statement. Focus on your main arguments and key evidence.
        Keep your response under 130 words and maintain a {style} tone throughout."""
    ),
    
    "rebuttal": PromptTemplate(
        input_variables=["topic", "stance", "style", "previous_argument"],
        template="""As a {stance} debater responding to: "{previous_argument}"
        
        Provide a {style} rebuttal in the debate about '{topic}'.
        Address the key points made by your opponent while advancing your position.
        Keep your response under 130 words."""
    ),
    
    "closing": PromptTemplate(
        input_variables=["topic", "stance", "style", "debate_history"],
        template="""As a {stance} debater in a {style} debate about '{topic}',
        provide a closing statement. Consider this debate history:
        {debate_history}
        
        Summarize your key points and address major counterarguments.
        Keep your response under 130 words."""
    )
}