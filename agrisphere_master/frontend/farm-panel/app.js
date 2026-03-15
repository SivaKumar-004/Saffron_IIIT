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
    const cropInput = document.getElementById('crop-input');
    
    const valRecommendation = document.getElementById('val-recommendation');
    const recHeader = document.getElementById('rec-header');

    // WebSocket Setup
    const wsHost = window.location.hostname || 'localhost';
    const wsPort = window.location.port || '8000';
    const wsUrl = `ws://${wsHost}:${wsPort}/ws/dashboard`;
    
    let ws;
    let isConnected = false;
    let mockInterval = null;

    function startMockData() {
        if (mockInterval) return;
        mockInterval = setInterval(() => {
            if (isConnected) return;
            const crop = cropInput.value || 'Tomato';
            
            // Generate mock data to simulate hardware
            const moisture = (Math.random() * 20 + 30).toFixed(1); // 30-50%
            const temp = (Math.random() * 10 + 20).toFixed(1); // 20-30C
            const humidity = (Math.random() * 20 + 40).toFixed(1); // 40-60%
            
            animateValue(valMoisture, moisture, '%');
            animateValue(valTemperature, temp, '°C');
            animateValue(valHumidity, humidity, '%');
            
            valClimateRisk.innerText = "Moderate (Mocked)";
            valClimateRisk.style.color = 'var(--accent-yellow)';
            animateValue(valRainfall, "12", 'mm');
            
            valPlantStatus.innerText = `Optimal for ${crop}.`;
            
            recHeader.innerText = "Local Simulation Result:";
            valRecommendation.innerText = "Hardware disconnected. Running in simulation mode to produce mock hardware data.";
        }, 3000);
    }
    
    function stopMockData() {
        if (mockInterval) {
            clearInterval(mockInterval);
            mockInterval = null;
        }
    }

    cropInput.addEventListener('change', () => {
        const crop = cropInput.value || 'Tomato';
        
        if (isConnected && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'set_crop', crop: crop }));
        }

        // Instantly generate and display random demo values over the UI for immediate responsiveness
        const moisture = (Math.random() * 20 + 30).toFixed(1); 
        const temp = (Math.random() * 10 + 20).toFixed(1); 
        const humidity = (Math.random() * 20 + 40).toFixed(1); 
        
        animateValue(valMoisture, moisture, '%');
        animateValue(valTemperature, temp, '°C');
        animateValue(valHumidity, humidity, '%');
        
        const risks = ["High Wind", "Heavy Rain", "Drought", "Normal"];
        const randomRisk = risks[Math.floor(Math.random() * risks.length)];
        valClimateRisk.innerText = randomRisk;
        valClimateRisk.style.color = randomRisk === "Normal" ? 'var(--accent-green)' : 'var(--accent-yellow)';
        
        animateValue(valRainfall, (Math.random() * 50).toFixed(1), 'mm');
        
        valPlantStatus.innerText = `Optimal for ${crop}.`;
        recHeader.innerText = "Multi Agent Result:";
        valRecommendation.innerText = `[Smart Plant Agent] Calculated simulated growth parameters for ${crop}. Data updated instantly.`;
    });

    function connect() {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            stopMockData();
            statusDot.classList.add('connected');
            statusText.innerText = 'System Online - Live Stream';
            
            // Send initial crop
            if (cropInput.value) {
                ws.send(JSON.stringify({ type: 'set_crop', crop: cropInput.value }));
            }
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
            isConnected = false;
            statusDot.classList.remove('connected');
            statusText.innerText = 'Offline - Running Simulation...';
            startMockData();
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
        animateValue(valTemperature, sensor.data.temperature, '°C');
        animateValue(valHumidity, sensor.data.humidity, '%');

        // Update Climate
        const risks = climate.data.risks || [];
        const riskText = risks.length > 0 ? risks.join(', ') : 'Normal';
        valClimateRisk.innerText = riskText;
        animateValue(valRainfall, climate.data.rainfall, 'mm');
        
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
        recHeader.innerText = "Multi Agent Result:";
        valRecommendation.innerText = `[${currentRec.agent}] ${currentRec.text}`;
        recCycle++;

        // Color coding for climate risk
        if (riskText !== 'Normal') {
            valClimateRisk.style.color = 'var(--accent-red)';
        } else {
            valClimateRisk.style.color = 'var(--accent-green)';
        }
    }

    connect();
});
