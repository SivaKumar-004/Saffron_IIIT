document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    // Telemetry Elements
    const valMoisture = document.getElementById('val-moisture');
    const valTemperature = document.getElementById('val-temperature');
    const valHumidity = document.getElementById('val-humidity');
    
    // Climate Elements
    const valClimateRisk = document.getElementById('val-climate-risk');
    const valRainfall = document.getElementById('val-rainfall');
    
    // Plant Elements
    const valPlantStatus = document.getElementById('val-plant-status');
    
    const valRecommendation = document.getElementById('val-recommendation');
    const recHeader = document.getElementById('rec-header');

    // WebSocket Setup
    const wsHost = window.location.hostname || 'localhost';
    const wsPort = window.location.port || '8000';
    const wsUrl = `ws://${wsHost}:${wsPort}/ws/dashboard`;
    
    let ws;

    function connect() {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            statusDot.classList.add('connected');
            statusText.innerText = 'System Online - Live Stream';
        };

        ws.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                updateDashboard(payload);
            } catch (err) {
                console.error("Failed to parse websocket message", err);
            }
        };

        ws.onclose = () => {
            statusDot.classList.remove('connected');
            statusText.innerText = 'Offline - Reconnecting...';
            setTimeout(connect, 3000);
        };
    }

    function animateValue(element, newValue, suffix = '') {
        if (!element) return;
        element.innerHTML = `${newValue}<span class="unit">${suffix}</span>`;
        element.parentElement.classList.remove('update-anim');
        void element.parentElement.offsetWidth; 
        element.parentElement.classList.add('update-anim');
    }

    let recCycle = 0;
    function updateDashboard(payload) {
        const { sensor, climate, plant } = payload;

        // Update Telemetry
        animateValue(valMoisture, sensor.data.soil_moisture, '%');
        animateValue(valTemperature, sensor.data.soil_temperature, '°C');
        animateValue(valHumidity, sensor.data.humidity, '%');

        // Update Climate
        valClimateRisk.innerText = climate.data.risk;
        animateValue(valRainfall, climate.data.rainfall.replace('mm', ''), 'mm');
        
        // Update Plant
        valPlantStatus.innerText = plant.recommendation.split('.')[0]; // Short version

        // Recommendation Cycling Logic
        const recs = [
            { agent: "Climate Intelligence", text: climate.recommendation },
            { agent: "Farm Sensor Agent", text: sensor.recommendation },
            { agent: "Smart Plant Agent", text: plant.recommendation }
        ];

        // Pick one to display every update to keep the UI dynamic
        const currentRec = recs[recCycle % recs.length];
        recHeader.innerText = currentRec.agent + " says:";
        valRecommendation.innerText = currentRec.text;
        recCycle++;

        // Color coding for climate risk
        if (climate.data.risk !== 'Normal') {
            valClimateRisk.style.color = 'var(--accent-red)';
        } else {
            valClimateRisk.style.color = 'var(--accent-green)';
        }
    }

    connect();
});
