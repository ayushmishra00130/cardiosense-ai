const form = document.getElementById("risk-form");
const resultPanel = document.getElementById("result-panel");
const errorMessage = document.getElementById("error-message");
const riskBadge = document.getElementById("risk-badge");
const riskProbability = document.getElementById("risk-probability");
const baseProbability = document.getElementById("base-probability");
const recommendationList = document.getElementById("recommendation-list");
const predictButton = document.getElementById("predict-btn");

function collectPayload() {
    return {
        age: Number(document.getElementById("age").value),
        blood_pressure: Number(document.getElementById("blood_pressure").value),
        cholesterol: Number(document.getElementById("cholesterol").value),
        sex: document.getElementById("sex").value,
        chest_pain: document.getElementById("chest_pain").value,
        shortness_of_breath: document.getElementById("shortness_of_breath").checked,
        fatigue: document.getElementById("fatigue").checked,
        irregular_heartbeat: document.getElementById("irregular_heartbeat").checked,
        smoking: document.getElementById("smoking").value,
        diabetes: document.getElementById("diabetes").checked,
    };
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function hideError() {
    errorMessage.classList.add("hidden");
    errorMessage.textContent = "";
}

function updateBadge(risk) {
    riskBadge.textContent = risk;
    riskBadge.classList.remove("low", "medium", "high");
    riskBadge.classList.add(risk.toLowerCase());
}

function renderRecommendations(items) {
    recommendationList.innerHTML = "";
    items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        recommendationList.appendChild(li);
    });
}

async function predict(event) {
    event.preventDefault();
    hideError();
    resultPanel.classList.add("hidden");

    const payload = collectPayload();

    predictButton.disabled = true;
    predictButton.textContent = "Checking...";

    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || "Could not check risk. Please try again.");
        }

        updateBadge(result.risk);
        riskProbability.textContent = `${(result.risk_probability * 100).toFixed(1)}%`;
        baseProbability.textContent = `${(result.base_probability * 100).toFixed(1)}%`;
        renderRecommendations(result.recommendations || []);
        resultPanel.classList.remove("hidden");
    } catch (error) {
        showError(error.message || "Something went wrong. Please try again.");
    } finally {
        predictButton.disabled = false;
        predictButton.textContent = "Check My Risk";
    }
}

form.addEventListener("submit", predict);