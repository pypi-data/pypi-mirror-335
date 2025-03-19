import json
 
from typing import List, Dict, Any, Optional

class RedisMemory:
    """Redis-backed memory store for agent conversations"""
    
    def __init__(self, 
                 redis_client,  # Simplified to require a client
                 key_prefix: str = "agent:",
                 agent_id: str = None,
                 max_messages: int = 20,
                 ttl: int = 86400):  # Default 24 hour TTL
        """
        Initialize Redis memory store
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            agent_id: Unique ID for this agent (will be auto-generated if None)
            max_messages: Maximum number of messages to store
            ttl: Time-to-live in seconds for the conversation history
        """
        self.client = redis_client
        self.agent_id = agent_id or self._generate_id()
        self.key = f"{key_prefix}{self.agent_id}"
        self.max_messages = max_messages
        self.ttl = ttl
    
    def _generate_id(self) -> str:
        """Generate a unique ID for this conversation"""
        import uuid
        return str(uuid.uuid4())
    
    def add_message(self, role: str, content: str, name: Optional[str] = None) -> None:
        """Add a message to memory"""
        # Convert content to string if it's not already
        content = str(content) if not isinstance(content, str) else content
        
        # Create message object
        message = {"role": role, "content": content}
        if role == "function" and name:
            message["name"] = name
        
        # Load existing messages
        messages = self.get_messages()
        
        # Add new message
        messages.append(message)
        
        # Trim to max_messages
        if len(messages) > self.max_messages:
            messages = messages[-self.max_messages:]
        
        # Save to Redis with TTL
        self.client.setex(
            self.key,
            self.ttl,
            json.dumps(messages)
        )
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in memory"""
        data = self.client.get(self.key)
        if data:
            return json.loads(data)
        return []
    
    def clear(self) -> None:
        """Clear all messages"""
        self.client.delete(self.key)
    
    def set_ttl(self, ttl: int) -> None:
        """Update the TTL for this conversation"""
        if self.client.exists(self.key):
            self.client.expire(self.key, ttl)
        self.ttl = ttl


class RedisSessionManager:
    """Manages multiple conversation sessions in Redis"""
    
    def __init__(self, 
                 redis_client,  # Require the redis client
                 key_prefix: str = "agent:"):
        """
        Initialize Redis session manager
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
        """
        self.client = redis_client
        self.key_prefix = key_prefix
    
    def create_session(self, 
                      agent_id: str = None, 
                      max_messages: int = 20,
                      ttl: int = 86400) -> RedisMemory:
        """Create a new session or get an existing one"""
        return RedisMemory(
            redis_client=self.client,
            key_prefix=self.key_prefix,
            agent_id=agent_id,
            max_messages=max_messages,
            ttl=ttl
        )
    
    def list_sessions(self) -> List[str]:
        """List all active sessions"""
        keys = self.client.keys(f"{self.key_prefix}*")
        return [key.decode('utf-8').replace(self.key_prefix, '') 
                for key in keys]
    
    def delete_session(self, agent_id: str) -> bool:
        """Delete a session"""
        key = f"{self.key_prefix}{agent_id}"
        return bool(self.client.delete(key))
    
    def clear_all_sessions(self) -> int:
        """Clear all sessions"""
        keys = self.client.keys(f"{self.key_prefix}*")
        if keys:
            return self.client.delete(*keys)
        return 0