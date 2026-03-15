# Technical Documentation

## Architecture
AgriSphere operates as a modular multi-agent system built on FastAPI. The architecture strictly demands that all agents adhere to a unified response contract.

## Unified Response Contract
All agents MUST return the following identical schema structure:
```json
{
 "agent": "agent_name",
 "status": "ok",
 "data": {},
 "recommendation": ""
}
```

## Directory Layout
- `/backend/main.py`: The FastAPI server entrypoint exposing POST routes.
- `/backend/agents/main_agent.py`: The `process_query` orchestrator.
- `/backend/agents/climate_agent.py`: OpenWeather API logic (simulated).
- `/backend/agents/sensor_agent.py`: Emulates raw hardware metrics.
- `/backend/agents/plant_agent.py`: Urban gardening database and ruleset.
- `/frontend/`: Static Nginx volume hosting the simulation dashboard.

## Deployment Profile
- **Backend Memory Cap**: 512M
- **Frontend Memory Cap**: 128M
- **Database**: Ephemeral / No-SQL state simulation.
- **Network**: Bridge network connecting `agrisphere_frontend` -> `agrisphere_backend:8000`.
