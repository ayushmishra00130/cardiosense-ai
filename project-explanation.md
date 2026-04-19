# CardioSense AI - Full Project Explanation

## 1) What this project is

CardioSense AI is a heart-risk screening web application.
It takes user health information from a form, sends it to a backend API, and predicts heart disease risk using a supervised machine learning model.

The final output shown to the user includes:
- Risk category: Low, Medium, or High
- Risk probability
- Base model probability
- Practical preventive recommendations

Important: this is a screening support tool, not a medical diagnosis tool.

## 2) Project architecture (simple view)

The system has three parts:

1. Frontend (UI)
- Files: frontend/index.html, frontend/style.css, frontend/script.js
- Job: collect user input and show result

2. Backend API (Flask)
- File: backend/app.py
- Job: validate request, build model features, run prediction, return response JSON

3. ML training + feature logic
- Files: backend/train_model.py, backend/model.py
- Job: train model from dataset, prepare consistent feature engineering logic

Flow:
1. User fills form in browser
2. JavaScript sends POST request to /predict
3. Backend converts input to model-ready features
4. Saved model predicts probability
5. Backend classifies risk and generates recommendations
6. Frontend renders risk output

## 3) Dataset used and target

Dataset file:
- backend/heart.csv

About the data:
- It contains common heart-related clinical fields
- Your file uses target column name num (not target)

How target is handled:
- In training, num is converted to binary label:
  - num = 0 -> class 0 (lower risk side)
  - num > 0 -> class 1 (higher risk side)

Why this is done:
- The app returns Low/Medium/High screening categories from a binary model probability using thresholds and calibration logic.

## 4) Model training theory and implementation

Training script:
- backend/train_model.py

Key steps:

1. Load dataset
- Read CSV from heart.csv

2. Normalize schema
- Handle naming differences like thalch vs thalach

3. Select model feature columns
- Use a fixed feature schema for consistency

4. Encode categorical columns
- Convert categories to machine-readable values

5. Build preprocessing pipeline
- Use ColumnTransformer
- OneHotEncoder for categorical fields
- Pass-through for numeric fields

6. Model training
- Use RandomForestClassifier
- Split data into train/test style partitions
- Fit model on training split

7. Save model
- Export trained pipeline to backend/model.pkl

Why pipeline is important:
- It ensures same preprocessing logic is used at prediction time
- Reduces training/inference mismatch bugs

## 5) Backend feature engineering (core logic)

File:
- backend/model.py

This file is the heart of runtime logic. It does:

1. Schema constants
- Defines feature columns and category maps

2. Input normalization
- Converts text/boolean/numeric user values to expected types

3. Questionnaire-to-model conversion
- The UI asks practical questions (smoking, fatigue, shortness of breath, etc.)
- Dataset expects clinical model fields
- So helper logic maps user questionnaire into model-compatible features

4. Derived feature estimation
- Some dataset-style fields are estimated from questionnaire context
- This keeps frontend simple while model remains compatible with the trained dataset format

5. Probability adjustment
- Base model probability is adjusted using practical risk context
- Factors include diabetes, smoking, symptoms, high blood pressure, high cholesterol
- Final value is clipped to a safe range

6. Risk band conversion
- Probability -> Low / Medium / High based on thresholds

7. Recommendation generation
- Returns risk-specific and context-specific preventive suggestions

## 6) API design and processing

Main API file:
- backend/app.py

Endpoint:
- POST /predict

Request fields expected:
- age
- blood_pressure
- cholesterol
- sex
- chest_pain
- shortness_of_breath
- fatigue
- irregular_heartbeat
- smoking
- diabetes

What backend does on request:
1. Read JSON payload
2. Validate required fields
3. Build model features via backend/model.py
4. Load and run model from model.pkl
5. Compute base probability (predict_proba)
6. Apply adjustment logic
7. Convert to risk label
8. Generate recommendations
9. Return structured JSON

Response fields:
- risk
- risk_probability
- base_probability
- recommendations

## 7) Frontend form and output flow

Frontend files:
- frontend/index.html
- frontend/script.js
- frontend/style.css

How form works:
1. HTML has input fields and checkboxes for required user data
2. On submit, script.js collects all values
3. JavaScript sends fetch POST request to backend /predict
4. Waits for response JSON
5. Updates result panel with:
- Risk badge (Low/Medium/High)
- Estimated risk percentage
- Base model score
- Recommendation list
6. Handles errors with user-friendly messages

## 8) UI/UX sections implemented

The page contains:
- Top navigation
- Hero section
- Steps cards
- Assessment card (form + result)
- Separate Guide card (magazine style)
  - Now / Today / Every Week blocks
  - Do / Don't table
- Footer emergency note (subtle style)

Why this helps:
- Users can both assess and learn in the same flow
- Preventive guidance is separated into its own card for readability

## 9) Practical ML theory in easy words

1. Supervised learning
- Model learns from old examples where output is known

2. Classification
- Model predicts class tendency (risk side) from inputs

3. Probability output
- Model gives a probability-like confidence score
- This is not certainty, but a useful screening signal

4. Feature engineering
- Raw user answers are transformed into model inputs
- Good feature engineering improves practical usability

5. Calibration-like adjustment
- Domain-aware adjustments make output more realistic for questionnaire context

## 10) Why this design is useful for your goal

Your goal required:
- Symptom + lifestyle-based form
- ML risk prediction from standard dataset
- Low/Medium/High output
- Preventive recommendations

This project satisfies that by:
- Using a trained classifier from heart.csv
- Mapping real-world user questions into model feature space
- Returning risk + recommendations clearly in frontend

## 11) Limitations and responsible use

Important limitations:
- This does not replace ECG, blood tests, imaging, or doctor diagnosis
- Estimated/derived features are approximations for screening compatibility
- Different datasets/populations can affect generalization

Responsible use:
- Treat as awareness and triage support only
- For chest pain or emergency symptoms, seek immediate medical care

## 12) How to run end-to-end

From project root:

1. Install dependencies
- cd backend
- python -m pip install -r requirements.txt

2. Train model
- python train_model.py

3. Run backend
- python app.py

4. Open frontend
- Open frontend/index.html in browser

5. Test flow
- Fill form
- Click Check My Risk
- Review risk output and guide section

## 13) Summary

CardioSense AI combines:
- A practical questionnaire UI
- A trained ML classification pipeline
- Runtime feature engineering
- Clear risk communication and prevention guidance

So users get an understandable heart-risk screening experience with actionable next steps.
