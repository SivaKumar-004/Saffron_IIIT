// Select DOM Elements
const regionInput = document.getElementById('regionInput');
const searchBtn = document.getElementById('searchBtn');
const simulateBtn = document.getElementById('simulateBtn');
const loader = document.getElementById('loader');
const resultsCard = document.getElementById('resultsCard');
const errorBox = document.getElementById('errorBox');

// Call Simulator elements
const callInput = document.getElementById('callInput');
const sendCallBtn = document.getElementById('sendCallBtn');
const callResponseBox = document.getElementById('callResponseBox');
const callResponseText = document.getElementById('callResponseText');

// Results elements
const resultRegion = document.getElementById('resultRegion');
const valTemp = document.getElementById('valTemp');
const valHumidity = document.getElementById('valHumidity');
const valRain = document.getElementById('valRain');
const valWind = document.getElementById('valWind');
const risksList = document.getElementById('risksList');
const recommendationText = document.getElementById('recommendationText');

const dispatchBox = document.getElementById('dispatchBox');
const dispatchMethod = document.getElementById('dispatchMethod');
const dispatchLog = document.getElementById('dispatchLog');
const dispatchMetrics = document.getElementById('dispatchMetrics');

const API_BASE_URL = 'http://localhost:8000/api/climate';

// Helper to show/hide elements
const setVisibility = (element, show) => {
  if (show) {
    element.classList.remove('hidden');
    // Add fade-in animation trigger if not native
    element.style.animation = 'none';
    element.offsetHeight; /* trigger reflow */
    element.style.animation = null;
  } else {
    element.classList.add('hidden');
  }
};

const displayData = (data, recommendation) => {
  resultRegion.textContent = data.region;
  valTemp.textContent = `${data.temperature}°C`;
  valHumidity.textContent = `${data.humidity}%`;
  valRain.textContent = `${data.rainfall} mm`;
  valWind.textContent = `${data.wind_speed} km/h`;

  // Update risks
  risksList.innerHTML = '';
  if (data.risks && data.risks.length > 0) {
    data.risks.forEach(risk => {
      const li = document.createElement('li');
      li.textContent = risk;
      li.className = 'risk-badge';
      risksList.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.textContent = "None";
    li.className = 'risk-badge safe';
    risksList.appendChild(li);
  }

  recommendationText.textContent = recommendation;

  if (data.alert_dispatch) {
    dispatchMethod.textContent = data.alert_dispatch.dispatch_method;
    dispatchLog.textContent = data.alert_dispatch.dispatch_log;

    if (data.alert_dispatch.alert_triggered) {
      dispatchBox.classList.remove('inactive');
      dispatchMetrics.textContent = `Farmers Reached via SIM/SMS: ~${data.alert_dispatch.farmers_reached}`;
    } else {
      dispatchBox.classList.add('inactive');
      dispatchMetrics.textContent = "";
    }
  }

  setVisibility(loader, false);
  setVisibility(resultsCard, true);
};

const fetchClimateData = async (simulate = false) => {
  const region = regionInput.value.trim();

  if (!simulate && !region) {
    showError("Please enter a region name.");
    return;
  }

  // UI Setup
  setVisibility(errorBox, false);
  setVisibility(resultsCard, false);
  setVisibility(loader, true);

  try {
    let response;
    if (simulate) {
      response = await axios.get(`${API_BASE_URL}/simulate`);
    } else {
      response = await axios.get(API_BASE_URL, { params: { region } });
    }

    const payload = response.data;
    if (payload.status === "ok") {
      // Pass the extra dispatch object in
      const renderData = { ...payload.data, alert_dispatch: payload.alert_dispatch };
      displayData(renderData, payload.recommendation);
    } else {
      showError("Unexpected error from server.");
    }
  } catch (error) {
    setVisibility(loader, false);
    showError(error.response?.data?.detail || "Failed to fetch data. Is the backend running?");
  }
};

const showError = (msg) => {
  errorBox.textContent = msg;
  setVisibility(errorBox, true);
};

// Event Listeners
searchBtn.addEventListener('click', () => fetchClimateData(false));
simulateBtn.addEventListener('click', () => fetchClimateData(true));
regionInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    fetchClimateData(false);
  }
});

sendCallBtn.addEventListener('click', async () => {
  const transcript = callInput.value.trim();
  if (!transcript) return;

  sendCallBtn.textContent = 'Processing...';
  sendCallBtn.disabled = true;
  setVisibility(callResponseBox, false);

  try {
    const response = await axios.post('http://localhost:8000/api/call', { transcript });
    callResponseText.textContent = response.data.reply;
    setVisibility(callResponseBox, true);
  } catch (error) {
    showError("Failed to process call. " + (error.response?.data?.detail || ""));
  } finally {
    sendCallBtn.textContent = 'Process Call via AI';
    sendCallBtn.disabled = false;
  }
});
