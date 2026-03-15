# System Workflow

AgriSphere follows a continuous loop architecture for data ingestion and response.

## 1. Data Generation (Sensor Agent)
The `sensor_agent.py` simulates hardware metrics (moisture, temperature, humidity). These values drive the logic for higher-tier agents.

## 2. Orchestration (FastAPI Main)
The `main.py` orchestrator runs a non-blocking `while True` loop.
- It calls the **Sensor Agent** for raw metrics.
- It passes these metrics to the **Plant Agent** to determine specific crop health.
- It concurrently calls the **Climate Agent** to check for environmental risks.

## 3. Streaming (WebSocket)
The consolidated results are pushed through the `/ws/dashboard` socket to all connected clients.

## 4. UI Update (Frontend)
The `app.js` listener:
- Parses the multi-agent JSON.
- Updates the telemetry cards (Moisture, Temp, Humidity).
- Updates the climate risk status.
- Updates the crop health recommendation.
- Cycles through detailed agent tips in the recommendation panel to keep the user informed.
