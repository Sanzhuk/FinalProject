from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.transport import TransportResponse
from app.services.auth import get_current_active_user
from app.services.transport import get_user_transports

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/me/transports")
async def read_user_transports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_user_transports(db=db, user_id=current_user.id)


@router.post("/me/make-owner", response_model=UserResponse)
async def make_user_owner(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Make the current user a transport owner if they aren't already."""
    if current_user.is_owner:
        return current_user
    
    current_user.is_owner = True
    db.commit()
    db.refresh(current_user)
    
    return current_user 