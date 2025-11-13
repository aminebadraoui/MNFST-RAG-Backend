"""
Streaming utilities for Server-Sent Events (SSE)
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from uuid import UUID


async def stream_response_as_sse(
    response_content: str,
    message_id: UUID,
    chunk_size: int = 3,
    delay: float = 0.1
) -> AsyncGenerator[str, None]:
    """
    Stream a response as Server-Sent Events (SSE)
    
    Args:
        response_content: The content to stream
        message_id: The message ID for the response
        chunk_size: Number of words per chunk
        delay: Delay between chunks in seconds
        
    Yields:
        SSE formatted strings
    """
    # Send start event
    start_event = {
        "type": "start",
        "messageId": str(message_id)
    }
    yield f"data: {json.dumps(start_event)}\n\n"
    
    # Split content into words and stream in chunks
    words = response_content.split()
    current_chunk = []
    
    for i, word in enumerate(words):
        current_chunk.append(word)
        
        # Send chunk when we reach chunk_size or at the end
        if len(current_chunk) >= chunk_size or i == len(words) - 1:
            chunk_content = " ".join(current_chunk)
            
            token_event = {
                "type": "token",
                "content": chunk_content + (" " if i < len(words) - 1 else "")
            }
            yield f"data: {json.dumps(token_event)}\n\n"
            
            # Add delay between chunks for realistic streaming effect
            await asyncio.sleep(delay)
            current_chunk = []
    
    # Send end event
    end_event = {
        "type": "end",
        "messageId": str(message_id)
    }
    yield f"data: {json.dumps(end_event)}\n\n"


async def stream_error_as_sse(error_message: str) -> AsyncGenerator[str, None]:
    """
    Stream an error as Server-Sent Events (SSE)
    
    Args:
        error_message: The error message to stream
        
    Yields:
        SSE formatted error string
    """
    error_event = {
        "type": "error",
        "error": error_message
    }
    yield f"data: {json.dumps(error_event)}\n\n"