# Pydantic models for input and output payloads

from pydantic import BaseModel, Field
from typing import List, Optional


class Message(BaseModel):
    """Individual message in the WhatsApp conversation."""
    id: str
    body: str
    fromMe: bool
    timestamp: int


class WebhookPayload(BaseModel):
    """Payload we receive from SpicyTool when a WhatsApp message arrives."""
    chatBotId: str
    userEmail: str
    clientNumber: str
    from_: str = Field(alias="from") # "from" is a reserved word in Python
    contactId: str
    assignedContainer: str
    conversation: List[Message]

    class Config:
        populate_by_name = True


class WhatsAppOutgoingMessage(BaseModel):
    """Payload to send a message to WhatsApp via SpicyTool."""
    userEmail: str
    conversationId: str
    message: str


class AgentResponse(BaseModel):
    """Parsed agent response."""
    message: str
    should_escalate: bool = False


class WebhookResponse(BaseModel):
    """Response returned by our webhook."""
    status: str
    message_sent: Optional[str] = None
    whatsapp_api_status: Optional[int] = None
    should_escalate: bool = False
    escalation: Optional[dict] = None