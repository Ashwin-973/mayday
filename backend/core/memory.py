"""
Conversation memory management.
Maintains intent-scoped conversation state with slot tracking.
Simple in-memory storage - no vector databases or embeddings.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ConversationState:
    """
    Represents the state of a single conversation session.
    
    Memory is intent-scoped: when the user switches intent,
    slot data is reset to avoid context bleed.
    """
    session_id: str
    active_intent: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)
    slot_completion_status: Dict[str, bool] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def reset_slots(self):
        """Clear all slot data and completion status."""
        self.slots.clear()
        self.slot_completion_status.clear()
        self.last_updated = datetime.now()
    
    def update_intent(self, new_intent: str):
        """
        Update active intent.
        If intent changed, reset slots to avoid context bleed.
        """
        if self.active_intent != new_intent:
            self.reset_slots()
            self.active_intent = new_intent
            self.last_updated = datetime.now()
    
    def update_slots(self, new_slots: Dict[str, Any]):
        """Merge new slots into existing slots."""
        self.slots.update(new_slots)
        self.last_updated = datetime.now()
    
    def mark_slot_complete(self, slot_name: str, is_complete: bool = True):
        """Mark a slot as complete or incomplete."""
        self.slot_completion_status[slot_name] = is_complete
        self.last_updated = datetime.now()
    
    def is_slot_complete(self, slot_name: str) -> bool:
        """Check if a slot is marked as complete."""
        return self.slot_completion_status.get(slot_name, False)
    
    def get_slot(self, slot_name: str, default: Any = None) -> Any:
        """Get a slot value with optional default."""
        return self.slots.get(slot_name, default)


class ConversationMemory:
    """
    Manages conversation states for multiple sessions.
    Simple in-memory dictionary storage.
    """
    
    def __init__(self):
        self._states: Dict[str, ConversationState] = {}
    
    def get_state(self, session_id: str) -> ConversationState:
        """
        Get or create conversation state for a session.
        """
        if session_id not in self._states:
            self._states[session_id] = ConversationState(session_id=session_id)
        return self._states[session_id]
    
    def clear_session(self, session_id: str):
        """Remove a session from memory."""
        if session_id in self._states:
            del self._states[session_id]
    
    def clear_all(self):
        """Clear all sessions (useful for testing)."""
        self._states.clear()


# Global memory instance (singleton pattern)
_memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    """Get the global conversation memory instance."""
    return _memory
