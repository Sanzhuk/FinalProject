from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os
from starlette.responses import RedirectResponse, HTMLResponse

from app.api import auth, transport, users, chat
from app.db.database import engine, get_db
from app.models import user, transport as transport_model
from app.services.auth import get_current_active_user, get_current_user
from app.services.transport import get_transports, get_transport_by_id, get_user_transports

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

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(transport.router)
app.include_router(users.router)
app.include_router(chat.router)

templates = Jinja2Templates(directory="templates")

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
    return templates.TemplateResponse("add_transport.html", {"request": request})

@app.get("/transports/{transport_id}/edit")
async def edit_transport_page(
    request: Request,
    transport_id: int,
    db: Session = Depends(get_db)
):
    transport_item = get_transport_by_id(db=db, transport_id=transport_id)
    
    if not transport_item:
        raise HTTPException(status_code=404, detail="Transport not found")
    
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
    return templates.TemplateResponse("my_transports.html", {
        "request": request,
        "transports": [] 
    })

@app.get("/api")
async def api_root():
    return {"message": "Welcome to the Agricultural Transport Rental Platform API"}

@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    return templates.TemplateResponse("messages.html", {"request": request})

@app.get("/messages/{conversation_id}", response_class=HTMLResponse)
async def conversation_page(request: Request, conversation_id: int):
    return templates.TemplateResponse("conversation.html", {
        "request": request,
        "conversation_id": conversation_id
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 