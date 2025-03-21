"""
Agentrix: A framework for creating AI agents, agent managers and Memory stores.
"""

__version__ = "0.0.3"

# Core components
from .core import Tool, Agent, ManagerAgent, ChatMemory

# Redis memory components
from .redisModule import RedisMemory, RedisSessionManager

# JSON parser components
from .JsonParser import JsonModel, Field, JsonOutputParser, ValidationError

# Web scraper components
from .webScraper import WebScraper, web_scraper_tools, webpage_fetch_tool, webpage_links_tool

__all__ = [
    # Core components
    'Tool', 
    'Agent', 
    'ManagerAgent',
    'ChatMemory',
    
    # Redis memory components
    'RedisMemory', 
    'RedisSessionManager',
    
    # JSON parser components
    'JsonModel',
    'Field',
    'JsonOutputParser',
    'ValidationError',
    
    # Web scraper components
    'WebScraper',
    'web_scraper_tools',
    'webpage_fetch_tool',
    'webpage_links_tool'
]