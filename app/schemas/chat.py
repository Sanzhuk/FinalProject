from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True


class MessageWithSender(MessageResponse):
    sender_username: str
    is_owner: bool


class ConversationBase(BaseModel):
    transport_id: int


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int
    renter_id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    transport_name: str
    transport_image: Optional[str] = None
    renter_username: str
    owner_username: str
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0 