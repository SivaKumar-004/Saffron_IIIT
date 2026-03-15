from sqlalchemy import Column, String, Text
from app.database import Base
import uuid

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    session_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, index=True)
    scout_raw_data = Column(Text, nullable=True)
    analyst_structured_data = Column(Text, nullable=True)
    visionary_gaps = Column(Text, nullable=True)
