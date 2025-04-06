from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from app.models.chat import Conversation, Message
from app.models.transport import Transport
from app.models.user import User
from app.schemas.chat import ConversationCreate, MessageCreate


def get_conversations_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all conversations for a user (either as renter or owner)"""
    return db.query(Conversation)\
        .filter(or_(Conversation.renter_id == user_id, Conversation.owner_id == user_id))\
        .filter(Conversation.is_active == True)\
        .order_by(desc(Conversation.updated_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_conversation(db: Session, conversation_id: int):
    """Get a specific conversation by ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversation_by_transport_and_users(db: Session, transport_id: int, user_id: int, owner_id: int):
    """Get conversation between user and owner for a specific transport"""
    return db.query(Conversation)\
        .filter(Conversation.transport_id == transport_id)\
        .filter(Conversation.renter_id == user_id)\
        .filter(Conversation.owner_id == owner_id)\
        .first()


def create_conversation(db: Session, conversation: ConversationCreate, renter_id: int, owner_id: int):
    """Create a new conversation"""
    db_conversation = Conversation(
        transport_id=conversation.transport_id,
        renter_id=renter_id,
        owner_id=owner_id,
        is_active=True
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
    """Get messages for a conversation"""
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at)\
        .offset(skip)\
        .limit(limit)\
        .all()


def create_message(db: Session, message: MessageCreate, conversation_id: int, sender_id: int):
    """Create a new message in a conversation"""
    db_message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=message.content,
        is_read=False
    )
    db.add(db_message)
    
    # Update conversation's updated_at timestamp
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    # The updated_at will automatically update due to the onupdate trigger
    
    db.commit()
    db.refresh(db_message)
    return db_message


def mark_messages_as_read(db: Session, conversation_id: int, user_id: int):
    """Mark all messages in a conversation as read for a specific user"""
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .filter(Message.sender_id != user_id)\
        .filter(Message.is_read == False)\
        .all()
    
    for message in messages:
        message.is_read = True
    
    db.commit()
    return messages


def get_unread_message_count(db: Session, user_id: int):
    """Get total number of unread messages for a user across all conversations"""
    conversations = db.query(Conversation)\
        .filter(or_(Conversation.renter_id == user_id, Conversation.owner_id == user_id))\
        .filter(Conversation.is_active == True)\
        .all()
    
    unread_count = 0
    for conversation in conversations:
        unread_count += db.query(Message)\
            .filter(Message.conversation_id == conversation.id)\
            .filter(Message.sender_id != user_id)\
            .filter(Message.is_read == False)\
            .count()
    
    return unread_count


def get_unread_count_for_conversation(db: Session, conversation_id: int, user_id: int):
    """Get number of unread messages in a specific conversation for a user"""
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .filter(Message.sender_id != user_id)\
        .filter(Message.is_read == False)\
        .count()


def is_conversation_participant(db: Session, conversation_id: int, user_id: int):
    """Check if user is a participant in the conversation"""
    conversation = db.query(Conversation)\
        .filter(Conversation.id == conversation_id)\
        .filter(or_(Conversation.renter_id == user_id, Conversation.owner_id == user_id))\
        .first()
    
    return conversation is not None 