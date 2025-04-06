from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.transport import Transport
from app.schemas.transport import TransportCreate, TransportUpdate, TransportFilter
from app.models.user import User
from typing import List, Optional


def get_transports(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    filter_params: Optional[TransportFilter] = None
):
    query = db.query(Transport)
    
    if filter_params:
        if filter_params.location:
            query = query.filter(Transport.location == filter_params.location)
        if filter_params.category:
            query = query.filter(Transport.category == filter_params.category)
        if filter_params.min_price is not None:
            query = query.filter(Transport.price_per_day >= filter_params.min_price)
        if filter_params.max_price is not None:
            query = query.filter(Transport.price_per_day <= filter_params.max_price)
    
    return query.offset(skip).limit(limit).all()


def get_transport_by_id(db: Session, transport_id: int):
    return db.query(Transport).filter(Transport.id == transport_id).first()


def get_user_transports(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transport).filter(Transport.owner_id == user_id).offset(skip).limit(limit).all()


def create_transport(db: Session, transport: TransportCreate, owner_id: int):
    db_transport = Transport(
        **transport.model_dump(),
        owner_id=owner_id
    )
    db.add(db_transport)
    db.commit()
    db.refresh(db_transport)
    return db_transport


def update_transport(db: Session, transport_id: int, transport_update: TransportUpdate):
    db_transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if db_transport:
        update_data = transport_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transport, key, value)
        db.commit()
        db.refresh(db_transport)
    return db_transport


def delete_transport(db: Session, transport_id: int):
    db_transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if db_transport:
        db.delete(db_transport)
        db.commit()
        return True
    return False


def is_transport_owner(db: Session, transport_id: int, user_id: int) -> bool:
    transport = db.query(Transport).filter(
        and_(Transport.id == transport_id, Transport.owner_id == user_id)
    ).first()
    return transport is not None 