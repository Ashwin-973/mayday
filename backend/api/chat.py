"""
Chat API endpoint.
Handles chat requests with streaming responses.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from agents.agent import process_message
from utils.validators import is_valid_session_id, sanitize_message


router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    session_id: str
    message: str


async def stream_response(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """
    Stream response chunks from agent.
    
    Args:
        session_id: Session ID
        message: User message
    
    Yields:
        Response chunks
    """
    async for chunk in process_message(session_id, message):
        yield chunk


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with streaming response.
    
    Args:
        request: Chat request with session_id and message
    
    Returns:
        StreamingResponse with text chunks
    """
    # Validate session ID
    if not is_valid_session_id(request.session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Sanitize message
    message = sanitize_message(request.message)
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Return streaming response
    return StreamingResponse(
        stream_response(request.session_id, message),
        media_type="text/plain"
    )
