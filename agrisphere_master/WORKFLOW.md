# Data Workflow

This document explains how a request traverses the AgriSphere system from the user interface to the sub-agents and back.

## 1. Initial Request
The frontend dashboard executes a periodic AJAX `POST` request (e.g. `POST /ask-agrisphere`) containing a JSON payload.

```json
{
  "query_type": "plant",
  "payload": {
    "plant_name": "tomato",
    "soil_moisture": 25.0
  }
}
```

## 2. API Ingress (`main.py`)
The FastAPI server running on Uvicorn receives the request at the endpoint matching the route. 
The request is validated against the `AgentRequest` Pydantic model. If valid, it is immediately passed into the `main_agent.py`.

## 3. Orchestration (`main_agent.py`)
The Main Agent checks the `query_type`. Based on the string, it delegates the payload to the corresponding agent script:
- `climate` -> `climate_agent.py`
- `farm` -> `sensor_agent.py`
- `plant` -> `plant_agent.py`

## 4. Sub-Agent Execution
The specific sub-agent processes the data. It applies its unique business logic (e.g. checking weather risks, rolling random sensor values, or looking up plant compatibility). It formats its findings into the strict Unified Response Contract.

## 5. Return Trip
The JSON payload travels back up the chain natively. FastAPI serializes the dictionary into a proper HTTP matching response, passing through the CORS middleware, and arriving at the Nginx frontend where the UI is updated dynamically.
