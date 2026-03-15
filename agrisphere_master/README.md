# AgriSphere: Master Integrated Platform

AgriSphere is a comprehensive, AI-driven agricultural intelligence platform. This repository contains the fully integrated "Master" version, combining advanced multi-agent backend logic with a stunning, modern Glassmorphism frontend interface.

## 🌟 Key Features

The platform is divided into three primary agricultural intelligence tiers, orchestrated by a central master agent.

*   **Master Orchestrator (Global Chatbot)**: A FastAPI WebSocket-driven brain (`/ws/master-chat`) that parses natural language farmer queries, intelligently routes them to the appropriate sub-agents concurrently, and synthesizes a unified AI response.
*   **Tier 1: Climate Intelligence**: Analyzes real-time weather data (via Open-Meteo) to predict flood, drought, and heatwave risks for specific regions. Features an Emergency Alert System and a deterministic logic fallback for ultimate reliability.
*   **Tier 2: Advanced Farm Telemetry**: A live dashboard that connects to precision farm sensors via WebSocket (`/ws/dashboard`). It streams synchronized real-time (and dynamically mocked) soil moisture, temperature, and climate data direct to the UI. Features dynamic crop input for instant, localized multi-agent recommendations.
*   **Tier 3: Urban Smart Plant**: Provides deep-dive plant care logic, optimal growing conditions, and companion planting suggestions databases.

## 💻 Architecture

*   **Backend**: Python FastAPI delivering both RESTful HTTP endpoints and high-speed Asynchronous WebSockets (`asyncio.gather`).
*   **Frontend**: High-performance Vanilla HTML/CSS/JS architecture heavily utilizing modern CSS Glassmorphism aesthetics, CSS Grid/Flexbox layouts, and dynamic DOM manipulation for real-time data rendering. Hosted via an Alpine Nginx container.
*   **AI Integration**: Powered by Google Gemini (`gemini-2.5-flash`) for advanced synthesis, with robust fallback mechanisms ensuring the platform remains fully functional even without API keys.

## 🚀 Quick Start / Deployment

AgriSphere is fully containerized for seamless deployment.

1.  **Prerequisites**: Ensure Docker Desktop (or Docker Engine + Compose) is installed and running on your machine.
2.  **Environment Variables (Optional)**: If you possess a Gemini API Key, place it in an `.env` file at the root or export it to enable the advanced LLM synthesis: `export GEMINI_API_KEY=your_key_here`. 
    *   *Note: If no key is provided, the system gracefully degrades to its built-in deterministic fallback logic.*
3.  **Build and Run**:
    ```bash
    docker-compose up --build -d
    ```
4.  **Access the Platform**:
    *   **Main Landing Page**: [http://localhost:80](http://localhost:80)
    *   **Climate Panel (Tier 1)**: [http://localhost:80/climate-panel](http://localhost:80/climate-panel)
    *   **Farm Dashboard (Tier 2)**: [http://localhost:80/farm-panel.html](http://localhost:80/farm-panel.html)
    *   **Smart Plant (Tier 3)**: [http://localhost:80/plant-panel](http://localhost:80/plant-panel)
    *   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ System Hardening & Security

This integration includes crucial security hardening measures:
- **Strict CORS Profiles**: Hardened FastAPI CORS middleware to prevent unauthorized origin access.
- **Input Validation & Sanitization**: Strengthened agent-level data typing using Pydantic schemas.
- **Graceful Error Handling**: Fallback mechanisms on all API routes to prevent internal server errors from halting the application, sending standardized `status: error` JSON payloads to the frontend instead.
- **WebSocket Reconnection Logic**: The client-side automatically handles dropped socket connections, transitioning smoothly to local simulation loops until the backend is restored.
