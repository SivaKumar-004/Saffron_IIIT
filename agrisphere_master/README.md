# AgriSphere Master

An AI-driven agricultural intelligence platform. This repository contains the fully integrated master version combining the efforts of all team members.

## Features
- **Core Orchestrator**: FastAPI backend that routes requests.
- **Climate Intelligence (Tier 1)**: Analyzes weather data to predict flood and drought risks.
- **Precision Farm Sensor (Tier 2)**: Simulates soil moisture and temperature for irrigation recommendations.
- **Urban Smart Plant (Tier 3)**: Provides plant care logic and companion planting suggestions.
- **Live Dashboard**: A frontend panel that polls the multi-agent system in real time.

## Quick Start
1. Ensure Docker Desktop is running.
2. Run `docker compose up --build -d`.
3. Open `http://localhost:80` in your browser to view the live Agent dashboard.
4. Interact with the backend APIs directly at `http://localhost:8000/docs`.
