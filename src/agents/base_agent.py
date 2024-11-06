# WON'T USE

from typing import List, Dict # to specify the type of data in the arguments and variables 
import time  # to fetch timestamp of arguments

class BaseAgent:
    """
    Base class for all agents in the debate system.
    Provides common functionality for memory and statistics tracking.
    May be I can have role as well for an agent
    """
    def __init__(self, name: str):
        self.name = name
        self.memory = []  # to hold the previous arguments/statements
        self.stats = {} #
        
    def remember(self, content: str, type: str):
        """Store information in agent's memory"""
        self.memory.append({
            "content": content,
            "type": type,  # argument or fact checking or any other type of statement made in the debate
            "timestamp": time.time()
        })
        
    def get_memory(self, memory_type: str = None) -> List[Dict]:
        """
        Retrieve memories, optionally filtered by type
        for the agents to retrieve past memories to moderate or conclude or for any other task
        """
        if memory_type:
            return [m for m in self.memory if m["type"] == memory_type]
        return self.memory

    def update_stats(self, stat_name: str, value: int = 1):
        """
        Update agent statistics
        Stats can be the number of arguments made or mistakes identified. Not crucial 
        """
        if stat_name not in self.stats:
            self.stats[stat_name] = 0  # Create a new statistics for agent performance
        self.stats[stat_name] += value
        
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        return self.stats