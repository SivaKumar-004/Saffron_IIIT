document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    const valMoisture = document.getElementById('val-moisture');
    const valTemperature = document.getElementById('val-temperature');
    const valHumidity = document.getElementById('val-humidity');
    const valLight = document.getElementById('val-light');
    const valRecommendation = document.getElementById('val-recommendation');
    const btnAnomaly = document.getElementById('btn-anomaly');
    const valAgentInsight = document.getElementById('val-agent-insight');

    // Attempt to connect to WebSocket on the same host (assuming standard port fallback to localhost:8000)
    // Adjusting for both cases: running frontend locally without server vs mounting to FastAPI directly.
    const wsHost = window.location.hostname || 'localhost';
    const wsPort = window.location.port || '8000';
    const wsUrl = `ws://${wsHost}:${wsPort}/ws/sensor-data`;
    
    let ws;

    function connect() {
        console.log(`Attempting connection to ${wsUrl}...`);
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            statusDot.classList.add('connected');
            statusText.innerText = 'Connected - Live Data';
        };

        ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                
                if (payload.status === 'ok') {
                    updateDashboard(payload.data, payload.recommendation);
                    // Update CrewAI Insights
                    if (payload.agent_insight && valAgentInsight.innerText !== payload.agent_insight) {
                        valAgentInsight.innerText = payload.agent_insight;
                        // Auto scroll to bottom of logs
                        valAgentInsight.scrollTop = valAgentInsight.scrollHeight;
                    }
                } else {
                    console.error("Agent returned error:", payload);
                    valRecommendation.innerText = payload.recommendation;
                    valRecommendation.style.color = 'var(--accent-red)';
                }
            } catch (err) {
                console.error("Failed to parse websocket message", err);
            }
        };

        ws.onclose = () => {
            statusDot.classList.remove('connected');
            statusText.innerText = 'Disconnected - Retrying...';
            // Auto reconnect every 3s
            setTimeout(connect, 3000);
        };

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err);
            ws.close();
        };
    }

    function animateValue(element, newValue, suffix = '') {
        element.innerHTML = `${newValue}<span class="unit">${suffix}</span>`;
        // Trigger micro-animation
        element.parentElement.classList.remove('update-anim');
        void element.parentElement.offsetWidth; // trigger reflow
        element.parentElement.classList.add('update-anim');
    }

    function updateDashboard(data, recommendation) {
        animateValue(valMoisture, data.soil_moisture, '%');
        animateValue(valTemperature, data.soil_temperature, '°C');
        animateValue(valHumidity, data.humidity, '%');
        
        // Handle Light special case (String)
        valLight.innerHTML = data.light_intensity;
        valLight.parentElement.classList.remove('update-anim');
        void valLight.parentElement.offsetWidth;
        valLight.parentElement.classList.add('update-anim');

        // Color coding based on recommendation
        valRecommendation.innerText = recommendation;
        
        const recCard = document.getElementById('card-recommendation');
        if (recommendation.includes('required today')) {
            valRecommendation.style.color = 'var(--accent-red)';
            recCard.style.borderLeftColor = 'var(--accent-red)';
        } else if (recommendation.includes('Monitor')) {
            valRecommendation.style.color = 'var(--accent-orange)';
            recCard.style.borderLeftColor = 'var(--accent-orange)';
        } else {
            recCard.style.borderLeftColor = 'var(--accent-green)';
        }
    }

    // Handle Anomaly Injection
    btnAnomaly.addEventListener('click', async () => {
        try {
            btnAnomaly.innerText = "Processing...";
            btnAnomaly.disabled = true;
            btnAnomaly.style.opacity = "0.5";
            
            const res = await fetch(`http://${wsHost}:${wsPort}/api/inject-anomaly`, { method: 'POST' });
            if(res.ok) {
                valAgentInsight.innerText += "\n\n[SYSTEM] Triggered Critical Drought Anomaly. CrewAI agents waking up to analyze...";
            }
        } catch (e) {
            console.error("Failed to inject anomaly", e);
        }
        setTimeout(() => {
            btnAnomaly.innerText = "⚠️ Force Drought Anomaly";
            btnAnomaly.disabled = false;
            btnAnomaly.style.opacity = "1";
        }, 5000);
    });

    // Initiate connection
    connect();
});
