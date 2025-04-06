from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
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
import shutil
import os
import uuid
from datetime import datetime

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
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    price_per_day: float = Form(...),
    year: Optional[int] = Form(None),
    model: Optional[str] = Form(None),
    capacity: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)
):
    """Create new transport with optional image upload"""
    
    image_url = None
    if image and image.filename:
        filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        file_path = os.path.join("static", "uploads", "transports", filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/static/uploads/transports/{filename}"
    
    transport_data = {
        "name": name,
        "description": description,
        "category": category,
        "location": location,
        "price_per_day": price_per_day,
        "year": year,
        "model": model,
        "capacity": capacity,
        "image_url": image_url
    }
    
    transport = TransportCreate(**transport_data)
    return create_transport(db=db, transport=transport, owner_id=current_user.id)


@router.put("/{transport_id}", response_model=TransportResponse)
async def update_transport_item(
    transport_id: int,
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    price_per_day: float = Form(...),
    year: Optional[int] = Form(None),
    model: Optional[str] = Form(None),
    capacity: Optional[str] = Form(None),
    existing_image_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update transport with optional image upload"""
    
    db_transport = get_transport_by_id(db, transport_id=transport_id)
    if db_transport is None:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    if not is_transport_owner(db, transport_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transport"
        )
    
    image_url = existing_image_url
    if image and image.filename:
        filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
        file_path = os.path.join("static", "uploads", "transports", filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/static/uploads/transports/{filename}"
    
    transport_data = {
        "name": name,
        "description": description,
        "category": category,
        "location": location,
        "price_per_day": price_per_day,
        "year": year,
        "model": model,
        "capacity": capacity,
        "image_url": image_url
    }
    
    transport_update = TransportUpdate(**transport_data)
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
    
    if not is_transport_owner(db, transport_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this transport"
        )
    
    delete_transport(db=db, transport_id=transport_id)
    return None 