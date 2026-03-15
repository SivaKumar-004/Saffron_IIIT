# Technical Documentation

## Architecture
AgriSphere - Saffron Edition is built on a high-concurrency **FastAPI** backend with specialized agents communicating via **WebSockets (Socket.io-style)** for real-time telemetry.

## Backend Stack
- **Framework**: FastAPI (Asynchronous Python)
- **Communication**: WebSockets (WS) for streaming, REST (POST) for direct agent queries.
- **Agents**: Decoupled Python modules in `/backend/agents/`.

## Security Hardening
- **CORS Restricted**: API only accepts requests from trusted local origins (`localhost`, `127.0.0.1`).
- **Input Validation**: Strict Pydantic models with `Field` constraints (e.g. `ge`, `le`, `pattern`, `max_length`).
- **Sanitization**: All agent inputs are length-limited and type-cast to prevent injection or DoS.
- **Error Isolation**: WebSocket stream uses isolated `try-except` blocks to ensure one failing agent doesn't crash the entire telemetry feed.
Streams a consolidated JSON payload every 3 seconds:
```json
{
  "sensor": { "agent": "sensor_agent", "data": { ... }, "recommendation": "..." },
  "climate": { "agent": "climate_agent", "data": { ... }, "recommendation": "..." },
  "plant": { "agent": "plant_agent", "data": { ... }, "recommendation": "..." }
}
```

### REST: `POST /ask-agent`
Request:
```json
{
  "query_type": "plant",
  "payload": { "plant_name": "tomato", "soil_moisture": 25.0 }
}
```

## Frontend Stack
- **Philosophy**: Vanilla CSS/JS for maximum performance and ZERO dependencies.
- **Design System**: Glassmorphism with HSL-balanced color palettes.
- **Live Sync**: Uses native `WebSocket` API for real-time UI updates with micro-animations.
