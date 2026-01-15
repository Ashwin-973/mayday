"""
Conversation state dataclass.
Stores session-level conversation state.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class State:
    """
    Represents the state of a conversation.
    This is a simple wrapper around the ConversationState in core.memory
    for agent-specific state management.
    """
    session_id: str
    active_intent: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"State(session_id={self.session_id}, intent={self.active_intent}, slots={self.slots})"
