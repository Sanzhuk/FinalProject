from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.schemas.transport import TransportCreate, TransportResponse, TransportUpdate, TransportFilter
from app.services.transport import (
    get_transports, 
    get_transport_by_id, 
    create_transport, 
    update_transport, 
    delete_transport,
    is_transport_owner
)
from app.services.auth import get_current_active_user, get_current_owner

router = APIRouter(prefix="/api/transports", tags=["transports"])


@router.get("/", response_model=List[TransportResponse])
async def read_transports(
    location: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    filter_params = None
    if any([location, category, min_price, max_price]):
        filter_params = TransportFilter(
            location=location,
            category=category,
            min_price=min_price,
            max_price=max_price
        )
    return get_transports(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/{transport_id}", response_model=TransportResponse)
async def read_transport(transport_id: int, db: Session = Depends(get_db)):
    db_transport = get_transport_by_id(db, transport_id=transport_id)
    if db_transport is None:
        raise HTTPException(status_code=404, detail="Transport not found")
    return db_transport


@router.post("/", response_model=TransportResponse, status_code=status.HTTP_201_CREATED)
async def create_transport_item(
    transport: TransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)
):
    return create_transport(db=db, transport=transport, owner_id=current_user.id)


@router.put("/{transport_id}", response_model=TransportResponse)
async def update_transport_item(
    transport_id: int,
    transport_update: TransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_transport = get_transport_by_id(db, transport_id=transport_id)
    if db_transport is None:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    # Check if the current user is the owner of the transport
    if not is_transport_owner(db, transport_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transport"
        )
    
    return update_transport(db=db, transport_id=transport_id, transport_update=transport_update)


@router.delete("/{transport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transport_item(
    transport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_transport = get_transport_by_id(db, transport_id=transport_id)
    if db_transport is None:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    # Check if the current user is the owner of the transport
    if not is_transport_owner(db, transport_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this transport"
        )
    
    delete_transport(db=db, transport_id=transport_id)
    return None 