'''agents Folder to package'''
# from .base_agent import BaseAgent -- removing as base class is not required
from .llm import HFInferenceLLM

from .debate_agent import DebateAgent
from .moderator import ModeratorAgent
from .fact_checker import FactCheckerAgent
from .debate_system import DebateSystem

__all__ = ['DebateAgent', 'HFInferenceLLM', 'ModeratorAgent', 'FactCheckerAgent', 'DebateSystem']