from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import os
import google.generativeai as genai

from app.database import engine, Base, get_db
from app.models import ResearchSession

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Agent Microservices API", version="1.0.0")

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Configure CORS: Allow all origins, methods, headers for flexibility, especially behind Nginx
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Multi-Agent Microservices API"}

@app.get("/sessions/")
async def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ResearchSession).all()
    return sessions

@app.post("/sessions/")
async def create_session(topic: str, db: Session = Depends(get_db)):
    new_session = ResearchSession(topic=topic)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

class InsightRequest(BaseModel):
    sensor_data: str

@app.post("/sessions/{session_id}/generate-insight")
async def generate_insight(session_id: str, request: InsightRequest, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.scout_raw_data = request.sensor_data
    db.commit()
    
    # Generate insights using async Gemini call
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Analyze the following agricultural sensor data for topic: '{session.topic}'. Data: {request.sensor_data}. Provide structured insights and note any visionary gaps."
        response = await model.generate_content_async(prompt)
        insight_text = response.text
        
        session.analyst_structured_data = insight_text
        db.commit()
        db.refresh(session)
        
        return {"status": "success", "insights": insight_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
