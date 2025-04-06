from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os
from starlette.responses import RedirectResponse

from app.api import auth, transport, users
from app.db.database import engine, get_db
from app.models import user, transport as transport_model
from app.services.auth import get_current_active_user, get_current_user
from app.services.transport import get_transports, get_transport_by_id, get_user_transports

# Create the database tables
user.Base.metadata.create_all(bind=engine)
transport_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agricultural Transport Rental Platform",
    description="API for renting agricultural transport, where owners can post their transport with detailed information and users can browse and select options",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(auth.router)
app.include_router(transport.router)
app.include_router(users.router)

# Templates
templates = Jinja2Templates(directory="templates")

# HTML routes
@app.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/transports")
async def transports_page(
    request: Request,
    location: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    # Get all transports with filtering
    filter_params = None
    if any([location, category, min_price, max_price]):
        from app.schemas.transport import TransportFilter
        filter_params = TransportFilter(
            location=location,
            category=category,
            min_price=min_price,
            max_price=max_price
        )
    
    transports = get_transports(db, filter_params=filter_params)
    
    return templates.TemplateResponse("transports.html", {
        "request": request,
        "transports": transports
    })

@app.get("/transports/add")
async def add_transport_page(request: Request):
    # Authentication will be handled client-side
    return templates.TemplateResponse("add_transport.html", {"request": request})

@app.get("/transports/{transport_id}/edit")
async def edit_transport_page(
    request: Request,
    transport_id: int,
    db: Session = Depends(get_db)
):
    # Get the transport without enforcing authentication
    transport_item = get_transport_by_id(db=db, transport_id=transport_id)
    
    # Check if transport exists
    if not transport_item:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    # Authentication and ownership will be checked client-side
    return templates.TemplateResponse("edit_transport.html", {
        "request": request,
        "transport": transport_item
    })

@app.get("/transports/{transport_id}")
async def transport_detail_page(request: Request, transport_id: int, db: Session = Depends(get_db)):
    transport_item = get_transport_by_id(db=db, transport_id=transport_id)
    
    if not transport_item:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    return templates.TemplateResponse("transport_detail.html", {
        "request": request,
        "transport": transport_item
    })

@app.get("/my-transports")
async def my_transports_page(
    request: Request, 
    db: Session = Depends(get_db)
):
    # We don't enforce authentication at the template level
    # This allows the page to load and handle authentication status client-side
    # If the user is authenticated, their transports will be fetched via API
    return templates.TemplateResponse("my_transports.html", {
        "request": request,
        "transports": []  # Empty by default, will be loaded via API if authenticated
    })

@app.get("/api")
async def api_root():
    return {"message": "Welcome to the Agricultural Transport Rental Platform API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 