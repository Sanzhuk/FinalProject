from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.transport import Transport
from app.schemas.chat import ConversationCreate, ConversationDetail, ConversationResponse, MessageCreate, MessageResponse, MessageWithSender
from app.services.chat import (
    get_conversations_for_user, 
    get_conversation, 
    get_conversation_by_transport_and_users,
    create_conversation, 
    get_messages, 
    create_message, 
    mark_messages_as_read,
    get_unread_message_count,
    get_unread_count_for_conversation,
    is_conversation_participant
)
from app.services.transport import get_transport_by_id
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/conversations", response_model=List[ConversationDetail])
async def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all conversations for the current user"""
    conversations = get_conversations_for_user(db, current_user.id, skip, limit)
    
    result = []
    for conv in conversations:
        transport = get_transport_by_id(db, conv.transport_id)
        
        messages = get_messages(db, conv.id, 0, 1)
        last_message = messages[0] if messages else None
        
        unread_count = get_unread_count_for_conversation(db, conv.id, current_user.id)
        
        detail = ConversationDetail(
            id=conv.id,
            transport_id=conv.transport_id,
            renter_id=conv.renter_id,
            owner_id=conv.owner_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            is_active=conv.is_active,
            transport_name=transport.name,
            transport_image=transport.image_url,
            renter_username=conv.renter.username,
            owner_username=conv.owner.username,
            last_message=last_message,
            unread_count=unread_count
        )
        result.append(detail)
    
    return result


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new conversation about a transport"""
    transport = get_transport_by_id(db, conversation.transport_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    existing_conversation = None
    
    if transport.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't start a conversation about your own transport"
        )
    
    existing_conversation = get_conversation_by_transport_and_users(
        db, 
        transport.id, 
        current_user.id, 
        transport.owner_id
    )
    
    if existing_conversation:
        return existing_conversation
    
    return create_conversation(
        db, 
        conversation, 
        renter_id=current_user.id, 
        owner_id=transport.owner_id
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific conversation by ID"""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if not is_conversation_participant(db, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )
    
    transport = get_transport_by_id(db, conversation.transport_id)
    
    messages = get_messages(db, conversation.id, 0, 1)
    last_message = messages[0] if messages else None
    
    unread_count = get_unread_count_for_conversation(db, conversation.id, current_user.id)
    
    mark_messages_as_read(db, conversation.id, current_user.id)
    
    detail = ConversationDetail(
        id=conversation.id,
        transport_id=conversation.transport_id,
        renter_id=conversation.renter_id,
        owner_id=conversation.owner_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        is_active=conversation.is_active,
        transport_name=transport.name,
        transport_image=transport.image_url,
        renter_username=conversation.renter.username,
        owner_username=conversation.owner.username,
        last_message=last_message,
        unread_count=unread_count
    )
    
    return detail


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageWithSender])
async def read_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages for a specific conversation"""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if not is_conversation_participant(db, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )
    
    messages = get_messages(db, conversation_id, skip, limit)
    
    mark_messages_as_read(db, conversation_id, current_user.id)
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        message_with_sender = MessageWithSender(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            content=msg.content,
            created_at=msg.created_at,
            is_read=msg.is_read,
            sender_username=sender.username,
            is_owner=sender.id == conversation.owner_id
        )
        result.append(message_with_sender)
    
    return result


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def create_new_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new message in a conversation"""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if not is_conversation_participant(db, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )
    
    return create_message(db, message, conversation_id, current_user.id)


@router.get("/unread-count", response_model=int)
async def get_unread_messages_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the total number of unread messages for the current user"""
    return get_unread_message_count(db, current_user.id) 