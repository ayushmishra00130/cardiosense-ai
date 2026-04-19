from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS
from model import build_model_features, adjust_probability, classify_risk, generate_recommendations

app = Flask(__name__)
CORS(app)

# Load model
model = pickle.load(open("model.pkl", "rb"))

@app.route("/")
def home():
    return "CardioSense AI Running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "age",
        "blood_pressure",
        "cholesterol",
        "chest_pain",
        "shortness_of_breath",
        "fatigue",
        "irregular_heartbeat",
        "smoking",
        "diabetes",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    features, context = build_model_features(data)

    if hasattr(model, "predict_proba"):
        base_probability = float(model.predict_proba(features)[0][1])
    else:
        base_probability = float(model.predict(features)[0])

    adjusted_probability = adjust_probability(base_probability, context)
    risk = classify_risk(adjusted_probability)
    recommendations = generate_recommendations(risk, context)

    return jsonify(
        {
            "risk": risk,
            "risk_probability": round(adjusted_probability, 4),
            "base_probability": round(base_probability, 4),
            "recommendations": recommendations,
        }
    )

if __name__ == "__main__":
    app.run(debug=True)