document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    const valMoisture = document.getElementById('val-moisture');
    const valTemperature = document.getElementById('val-temperature');
    const valHumidity = document.getElementById('val-humidity');
    const valLight = document.getElementById('val-light');
    const valRecommendation = document.getElementById('val-recommendation');

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
            valRecommendation.style.color = 'var(--accent-green)';
            recCard.style.borderLeftColor = 'var(--accent-green)';
        }
    }

    // Initiate connection
    connect();
});
