import os
import pickle
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, session
from flask_cors import CORS
from xhtml2pdf import pisa

from model import (
    PayloadValidationError,
    adjust_probability,
    build_model_features,
    calculate_heart_age,
    classify_risk,
    derive_primary_drivers,
    generate_recommendations,
    summarize_risk_drivers,
    validate_assessment_payload,
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "cardiosense-dev-secret")
CORS(app)

with open(MODEL_PATH, "rb") as model_file:
    model = pickle.load(model_file)


def _run_prediction(raw_payload):
    payload = validate_assessment_payload(raw_payload)
    features, context = build_model_features(payload)

    if hasattr(model, "predict_proba"):
        base_probability = float(model.predict_proba(features)[0][1])
    else:
        base_probability = float(model.predict(features)[0])

    adjusted_probability = adjust_probability(base_probability, context)
    risk = classify_risk(adjusted_probability)

    heart_age, penalties = calculate_heart_age(
        actual_age=payload["age"],
        smoking=payload["smoking"],
        blood_pressure=payload["blood_pressure"],
        diabetes=payload["diabetes"],
    )

    primary_drivers = derive_primary_drivers(payload, context, limit=3)
    risk_summary = summarize_risk_drivers(adjusted_probability, primary_drivers)
    recommendations = generate_recommendations(risk, context)

    prediction = {
        "risk": risk,
        "risk_probability": round(adjusted_probability, 4),
        "base_probability": round(base_probability, 4),
        "heart_age": heart_age,
        "heart_age_penalties": penalties,
        "primary_drivers": primary_drivers,
        "risk_summary": risk_summary,
        "recommendations": recommendations,
        "assessed_at": datetime.utcnow().isoformat() + "Z",
    }

    return payload, prediction


def _error_response(exc):
    status_code = 422 if getattr(exc, "is_biological_outlier", False) else 400
    return (
        jsonify(
            {
                "error": str(exc),
                "error_type": "biological_outlier" if status_code == 422 else "validation",
            }
        ),
        status_code,
    )


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/assess")
def assess():
    return render_template("assess.html")


@app.route("/results")
def results():
    latest_assessment = session.get("latest_assessment")
    return render_template("results.html", latest_assessment=latest_assessment)


@app.route("/api/v1/latest-result")
def latest_result():
    latest_assessment = session.get("latest_assessment")
    if not latest_assessment:
        return jsonify({"error": "No assessment found in current session."}), 404
    return jsonify(latest_assessment)


@app.route("/api/v1/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    try:
        payload, prediction = _run_prediction(data)
    except PayloadValidationError as exc:
        return _error_response(exc)

    mode = (request.args.get("mode") or "").strip().lower()
    if mode != "simulation":
        session["latest_assessment"] = {
            "payload": payload,
            "prediction": prediction,
        }

    return jsonify(prediction)


@app.route("/api/v1/report", methods=["POST"])
def download_report():
    data = request.get_json(silent=True) or {}
    payload = data.get("payload")

    if not payload:
        latest_assessment = session.get("latest_assessment") or {}
        payload = latest_assessment.get("payload")

    if not payload:
        return jsonify({"error": "No assessment payload provided for report generation."}), 400

    try:
        validated_payload, prediction = _run_prediction(payload)
    except PayloadValidationError as exc:
        return _error_response(exc)

    report_context = {
        "generated_on": datetime.utcnow().strftime("%d %b %Y %H:%M UTC"),
        "payload": validated_payload,
        "prediction": prediction,
        "drivers": prediction["primary_drivers"],
        "recommendations": prediction["recommendations"],
    }

    html = render_template("report_pdf.html", report=report_context)

    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(html, dest=pdf_buffer, encoding="utf-8")
    if pdf_status.err:
        return jsonify({"error": "Failed to generate PDF report."}), 500

    pdf_buffer.seek(0)
    filename = f"CardioSense_Medical_Summary_{datetime.utcnow():%Y%m%d_%H%M%S}.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
