# Detailed Project Specs

## Detailed Agent Logic
### Sensor Agent
- **Simulation**: Random Uniform distribution for Moisture (10-60%) and Humidity (30-80%).
- **Logic**: Threshold-based recommendations (Irrigate if <30%).

### Climate Agent
- **Logic**: Evaluates rainfall and temperature extremes. 
- **Critical Thresholds**: Temp > 40°C triggers "Heat Wave", Rain > 80mm triggers "Flood Risk".

### Plant Agent (Tomato Context)
- **Logic**: Inherits moisture from Sensor Agent.
- **Companion Planting**: Performs a lookup in the `COMPATIBLE_PLANTS` dictionary (Tomato -> Basil, Marigold, Onion).

## Fine-grained Frontend Details
- **Micro-Animations**: Uses CSS `@keyframes pop` triggered by CSS class toggling in the JS `animateValue` function.
- **Responsiveness**: Flexbox/Grid hybrid layout. Collapses into a single-column view on viewports < 768px.
- **Visuals**: Uses `--accent-green`, `--accent-blue`, and `--accent-red` for context-aware color coding.

## Deployment Details
- Served via `uvicorn`.
- Frontend is mounted at `/` using `StaticFiles`, ensuring the entire app (API + Dashboard) runs on a single port (8000).
