"""
Conversation management module for handling chat history and metadata.
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
import uuid
from redis import Redis
from .models import ChatMessage, ConversationMetadata

class ConversationManager:
    """Manages chat conversations and their history."""
    
    def __init__(self, redis_client: Redis):
        """
        Initialize the conversation manager.
        
        Args:
            redis_client: Redis client instance for storing conversation data
        """
        self.redis = redis_client
        self.conversation_ttl = timedelta(days=30)  # Store conversations for 30 days
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        metadata = ConversationMetadata()
        
        # Store conversation metadata
        self.redis.setex(
            f"conv:meta:{conversation_id}",
            self.conversation_ttl,
            json.dumps(metadata.dict())
        )
        
        return conversation_id
    
    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            message: ChatMessage to add
        """
        # Get current messages
        messages_key = f"conv:msgs:{conversation_id}"
        current_messages = self.redis.get(messages_key)
        
        if current_messages:
            messages = json.loads(current_messages)
            messages.append(message.dict())
        else:
            messages = [message.dict()]
        
        # Store updated messages
        self.redis.setex(
            messages_key,
            self.conversation_ttl,
            json.dumps(messages)
        )
        
        # Update conversation metadata
        meta_key = f"conv:meta:{conversation_id}"
        metadata_json = self.redis.get(meta_key)
        if metadata_json:
            metadata = ConversationMetadata(**json.loads(metadata_json))
            metadata.updated_at = datetime.utcnow()
            
            # Auto-generate title if it's the first user message
            if not metadata.title and message.role == "user":
                metadata.title = message.content[:50] + "..."
            
            self.redis.setex(
                meta_key,
                self.conversation_ttl,
                json.dumps(metadata.dict())
            )
    
    def get_messages(self, conversation_id: str) -> List[ChatMessage]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of ChatMessage objects
        """
        messages_json = self.redis.get(f"conv:msgs:{conversation_id}")
        if not messages_json:
            return []
        
        messages = json.loads(messages_json)
        return [ChatMessage(**msg) for msg in messages]
    
    def get_metadata(self, conversation_id: str) -> Optional[ConversationMetadata]:
        """
        Get metadata for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            ConversationMetadata if found, None otherwise
        """
        metadata_json = self.redis.get(f"conv:meta:{conversation_id}")
        if not metadata_json:
            return None
        
        return ConversationMetadata(**json.loads(metadata_json))
    
    def list_conversations(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        List recent conversations with their metadata.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of conversation metadata
        """
        # Get all conversation keys
        keys = self.redis.keys("conv:meta:*")
        keys.sort(reverse=True)  # Sort by most recent
        
        # Apply pagination
        paginated_keys = keys[offset:offset + limit]
        
        conversations = []
        for key in paginated_keys:
            metadata_json = self.redis.get(key)
            if metadata_json:
                conversation_id = key.decode().split(":")[-1]
                metadata = json.loads(metadata_json)
                conversations.append({
                    "id": conversation_id,
                    **metadata
                })
        
        return conversations
    
    def update_summary(self, conversation_id: str, summary: str) -> None:
        """
        Update the summary of a conversation.
        
        Args:
            conversation_id: ID of the conversation
            summary: New summary text
        """
        meta_key = f"conv:meta:{conversation_id}"
        metadata_json = self.redis.get(meta_key)
        if metadata_json:
            metadata = ConversationMetadata(**json.loads(metadata_json))
            metadata.summary = summary
            metadata.updated_at = datetime.utcnow()
            
            self.redis.setex(
                meta_key,
                self.conversation_ttl,
                json.dumps(metadata.dict())
            )
    
    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation and all its data.
        
        Args:
            conversation_id: ID of the conversation to delete
        """
        self.redis.delete(
            f"conv:meta:{conversation_id}",
            f"conv:msgs:{conversation_id}"
        ) 