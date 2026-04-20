from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    
    # One-to-many relationship: one server has many metric records.
    metrics = relationship("Metric", back_populates="owner")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    server_id = Column(Integer, ForeignKey("servers.id"))
    
    owner = relationship("Server", back_populates="metrics")