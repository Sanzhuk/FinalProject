from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    category = Column(String, index=True)  # E.g., Tractor, Harvester, Truck
    location = Column(String, index=True)
    price_per_day = Column(Float, index=True)
    available = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    
    # Specifications
    year = Column(Integer, nullable=True)
    model = Column(String, nullable=True)
    capacity = Column(String, nullable=True)  # Could be weight, volume, etc.
    
    # Owner relationship (many-to-one)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transports")
    
    # Conversations relationship (one-to-many)
    conversations = relationship("Conversation", back_populates="transport", cascade="all, delete-orphan") 