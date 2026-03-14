import asyncio
import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure the agents module can be imported properly regardless of where this script is run
sys.path.append(os.path.dirname(__file__))
from agents.sensor_agent import analyze_farm

app = FastAPI(title="AgriSphere Real-Time API")

# Setup CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/sensor-data")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that continuously streams simulated sensor data to clients.
    """
    await websocket.accept()
    print("Client connected to sensor-data websocket.")
    try:
        while True:
            # Generate new simulated sensor data payload
            payload = analyze_farm()
            
            # Send the JSON payload down the socket
            await websocket.send_json(payload)
            
            # Delay before simulating the next reading
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"WebSocket Error: {e}")

# Mount frontend static files if the directory exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Frontend dashboard not found at {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the application using this block or `uvicorn main:app`
    uvicorn.run(app, host="0.0.0.0", port=8000)
