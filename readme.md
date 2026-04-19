# CardioSense AI

CardioSense AI is a Flask multi-page web application for cardiovascular risk screening.

It provides:
- Server-side routed pages for Home, Assessment Wizard, and Results Dashboard
- ML-based risk prediction with explainable primary drivers
- Heart-age estimation and preventive recommendations
- Real-time what-if simulation controls
- Downloadable clinical PDF summary

## Project Structure

- backend/app.py: Flask routes and API endpoints
- backend/model.py: validation, feature engineering, calibration, explainability, recommendations
- backend/train_model.py: training pipeline that saves model.pkl
- backend/templates/: Home, Assessment, Results, PDF templates
- backend/static/: shared CSS/JS for MPA UI behavior

## Setup

From project root:

```powershell
cd backend
python -m pip install -r requirements.txt
python train_model.py
python app.py
```

App URL:
- http://127.0.0.1:5000

## User Flow

1. Open the Home page at /.
2. Click Start Assessment and complete the 3-step questionnaire at /assess.
3. Review risk output, explainability, and simulation in /results.
4. Download the Medical Summary PDF from the results page.

## API Endpoints

- POST /api/v1/predict
- GET /api/v1/latest-result
- POST /api/v1/report

Legacy compatibility alias:
- POST /predict

## Data and Modeling Notes

- Dataset: backend/heart.csv
- Model pipeline: preprocessing + RandomForestClassifier
- Input validation includes Biological Outlier checks for age, blood pressure, and cholesterol
- Final risk score is calibrated from model output with clinical context adjustments

## Disclaimer

This project is a computational screening support tool and does not replace diagnosis by a licensed cardiologist.

## Troubleshooting

If dependencies fail to install:

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
