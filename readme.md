# CardioSense AI

CardioSense AI is a web application integrated with a supervised machine learning model for heart disease risk assessment.

The app collects user inputs including:
- Chest pain
- Shortness of breath
- Fatigue
- Irregular heartbeat
- Age
- Blood pressure
- Cholesterol
- Smoking habit
- Diabetes status

The backend processes these inputs, maps them into the trained heart-disease feature space, and computes a risk probability using a classification model trained on a standard heart disease dataset.

The system classifies users into:
- Low risk
- Medium risk
- High risk

It also returns preventive health recommendations based on the risk profile.

## Current Frontend Experience

The UI has the following sections:
- Header navigation: Check Symptoms, Guide, Get Help Now
- Hero area with Start Assessment CTA
- 3-step overview cards
- Assessment form card with model result panel
- Separate Heart Care Guide card with:
	- Now / Today / Every Week action blocks
	- Do / Don't comparison table

## Project Structure

- `backend/train_model.py`: trains and saves the ML pipeline to `model.pkl`
- `backend/model.py`: shared feature engineering, risk calibration, classification, and recommendation logic
- `backend/app.py`: Flask API with `/predict`
- `frontend/index.html`, `frontend/script.js`, `frontend/style.css`: web UI

## Backend Setup

From project root:

```powershell
cd backend
python -m pip install -r requirements.txt
python train_model.py
python app.py
```

Backend runs at:

`http://127.0.0.1:5000`

## Frontend Usage

Open `frontend/index.html` in a browser while backend is running, fill in inputs, and click **Check My Risk**.

Recommended flow:
1. Start backend server.
2. Open frontend page.
3. Complete the assessment form.
4. Review risk level, risk probability, and recommendations.
5. Check the Guide section for practical prevention and emergency actions.

## API Contract

### POST `/predict`

Example request body:

```json
{
	"age": 45,
	"blood_pressure": 130,
	"cholesterol": 220,
	"sex": "male",
	"chest_pain": "atypical angina",
	"shortness_of_breath": true,
	"fatigue": false,
	"irregular_heartbeat": false,
	"smoking": "former",
	"diabetes": false
}
```

Example response:

```json
{
	"risk": "Medium",
	"risk_probability": 0.581,
	"base_probability": 0.521,
	"recommendations": [
		"Schedule a preventive health check within the next 2-4 weeks.",
		"Monitor symptoms and blood pressure weekly and discuss trends with a doctor.",
		"This tool is a screening assistant and does not replace professional diagnosis."
	]
}
```

Possible `risk` values:
- Low
- Medium
- High

## Data and Modeling Notes

- Training dataset is `backend/heart.csv`.
- The pipeline uses preprocessing plus `RandomForestClassifier`.
- `backend/model.py` converts questionnaire inputs into model-compatible features.
- A calibrated adjustment is applied to produce a more practical screening probability.

## Important Disclaimer

This project is for educational and screening support purposes only.
It does not replace medical diagnosis, emergency care, or consultation with a qualified healthcare professional.

## Troubleshooting

If dependency install fails, try:

```powershell
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If model file is missing:

```powershell
cd backend
python train_model.py
```

If frontend cannot reach backend, confirm Flask is running at `http://127.0.0.1:5000`.
