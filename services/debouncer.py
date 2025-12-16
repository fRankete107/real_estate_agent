# Debouncing service to handle rapid consecutive messages

import asyncio
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PendingMessage:
    """Stores pending message data waiting to be processed."""
    phone_number: str
    message_text: str
    payload_data: dict
    timestamp: datetime
    task: Optional[asyncio.Task] = None


class Debouncer:
    """
    Debouncer for handling rapid consecutive messages.
    
    Waits for a pause in messages before processing.
    If new message arrives, resets the timer.
    """
    
    def __init__(self, delay_seconds: float = 2.0):
        """
        Initialize debouncer.
        
        Args:
            delay_seconds: Time to wait after last message before processing
        """
        self.delay_seconds = delay_seconds
        self.pending_messages: Dict[str, PendingMessage] = {}
        self.message_buffers: Dict[str, list] = {}  # Store multiple messages
    
    async def debounce(
        self,
        phone_number: str,
        message_text: str,
        payload_data: dict,
        process_callback: Callable[[str, str, dict], Any]
    ) -> Optional[Any]:
        """
        Debounce a message.
        
        Args:
            phone_number: User identifier
            message_text: The message content
            payload_data: Additional payload data
            process_callback: Async function to call when debounce completes
            
        Returns:
            None if debouncing (waiting), or callback result if processed
        """
        
        # Cancel existing pending task for this user
        if phone_number in self.pending_messages:
            pending = self.pending_messages[phone_number]
            if pending.task and not pending.task.done():
                pending.task.cancel()
                try:
                    await pending.task
                except asyncio.CancelledError:
                    pass
        
        # Add message to buffer
        if phone_number not in self.message_buffers:
            self.message_buffers[phone_number] = []
        self.message_buffers[phone_number].append(message_text)
        
        # Create new pending message
        pending = PendingMessage(
            phone_number=phone_number,
            message_text=message_text,
            payload_data=payload_data,
            timestamp=datetime.now()
        )
        
        # Create debounce task
        async def debounce_task():
            await asyncio.sleep(self.delay_seconds)
            
            # Combine all buffered messages
            combined_message = " ".join(self.message_buffers.get(phone_number, [message_text]))
            
            # Clear buffer
            self.message_buffers[phone_number] = []
            
            # Remove from pending
            if phone_number in self.pending_messages:
                del self.pending_messages[phone_number]
            
            # Execute callback
            return await process_callback(phone_number, combined_message, payload_data)
        
        # Store and start task
        pending.task = asyncio.create_task(debounce_task())
        self.pending_messages[phone_number] = pending
        
        # Return immediately (don't wait for debounce)
        return None
    
    async def debounce_and_wait(
        self,
        phone_number: str,
        message_text: str,
        payload_data: dict,
        process_callback: Callable[[str, str, dict], Any]
    ) -> Any:
        """
        Debounce a message and wait for result.
        
        Same as debounce() but waits for the task to complete.
        Use this when you need the response.
        """
        
        # Cancel existing pending task for this user
        if phone_number in self.pending_messages:
            pending = self.pending_messages[phone_number]
            if pending.task and not pending.task.done():
                pending.task.cancel()
                try:
                    await pending.task
                except asyncio.CancelledError:
                    pass
        
        # Add message to buffer
        if phone_number not in self.message_buffers:
            self.message_buffers[phone_number] = []
        self.message_buffers[phone_number].append(message_text)
        
        # Wait for debounce delay
        await asyncio.sleep(self.delay_seconds)
        
        # Check if this is still the latest message (no new messages arrived)
        # If buffer has more messages, we were superseded
        current_buffer = self.message_buffers.get(phone_number, [])
        
        if current_buffer and current_buffer[-1] == message_text:
            # This is the latest message, process all buffered messages
            combined_message = " ".join(current_buffer)
            
            # Clear buffer
            self.message_buffers[phone_number] = []
            
            # Remove from pending
            if phone_number in self.pending_messages:
                del self.pending_messages[phone_number]
            
            # Execute callback
            return await process_callback(phone_number, combined_message, payload_data)
        
        # Superseded by newer message, return None
        return None
    
    def get_pending_count(self) -> int:
        """Get number of pending messages."""
        return len(self.pending_messages)
    
    def is_pending(self, phone_number: str) -> bool:
        """Check if user has pending message."""
        return phone_number in self.pending_messages
    
    async def cancel_all(self):
        """Cancel all pending tasks."""
        for phone_number, pending in self.pending_messages.items():
            if pending.task and not pending.task.done():
                pending.task.cancel()
        self.pending_messages.clear()
        self.message_buffers.clear()


# Global debouncer instance
debouncer = Debouncer(delay_seconds=7.0)