import pandas as pd

FEATURE_COLUMNS = [
	"age",
	"sex",
	"cp",
	"trestbps",
	"chol",
	"fbs",
	"restecg",
	"thalach",
	"exang",
	"oldpeak",
	"slope",
	"ca",
	"thal",
]

CATEGORICAL_COLUMNS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "thal"]
NUMERIC_COLUMNS = [col for col in FEATURE_COLUMNS if col not in CATEGORICAL_COLUMNS]

CATEGORY_MAPS = {
	"sex": {"male": 1, "female": 0, "m": 1, "f": 0, 1: 1, 0: 0},
	"cp": {
		"typical angina": 0,
		"atypical angina": 1,
		"non-anginal": 2,
		"asymptomatic": 3,
		"typical": 0,
		"atypical": 1,
		"non_anginal": 2,
		"none": 3,
		0: 0,
		1: 1,
		2: 2,
		3: 3,
	},
	"fbs": {"true": 1, "false": 0, "yes": 1, "no": 0, True: 1, False: 0, 1: 1, 0: 0},
	"restecg": {
		"normal": 0,
		"st-t abnormality": 1,
		"lv hypertrophy": 2,
		"abnormal": 2,
		0: 0,
		1: 1,
		2: 2,
	},
	"exang": {"true": 1, "false": 0, "yes": 1, "no": 0, True: 1, False: 0, 1: 1, 0: 0},
	"slope": {"upsloping": 0, "flat": 1, "downsloping": 2, 0: 0, 1: 1, 2: 2},
	"thal": {
		"normal": 2,
		"fixed defect": 1,
		"reversable defect": 3,
		"reversible defect": 3,
		1: 1,
		2: 2,
		3: 3,
	},
}


def _normalize_key(value):
	if isinstance(value, str):
		return value.strip().lower()
	return value


def _to_float(value, default):
	try:
		return float(value)
	except (TypeError, ValueError):
		return float(default)


def _to_bool(value):
	if isinstance(value, bool):
		return value
	if isinstance(value, (int, float)):
		return value != 0
	if isinstance(value, str):
		normalized = value.strip().lower()
		return normalized in {"1", "true", "yes", "y", "on", "current", "former"}
	return False


def _encode_with_map(value, mapping, default_value):
	direct = mapping.get(value)
	if direct is not None:
		return direct
	normalized = _normalize_key(value)
	mapped = mapping.get(normalized)
	if mapped is not None:
		return mapped
	return default_value


def build_model_features(payload):
	age = _to_float(payload.get("age"), 54)
	blood_pressure = _to_float(payload.get("blood_pressure"), 130)
	cholesterol = _to_float(payload.get("cholesterol"), 245)

	sex = _encode_with_map(payload.get("sex", "male"), CATEGORY_MAPS["sex"], 1)
	chest_pain = _encode_with_map(payload.get("chest_pain", "none"), CATEGORY_MAPS["cp"], 3)

	shortness_of_breath = _to_bool(payload.get("shortness_of_breath", False))
	fatigue = _to_bool(payload.get("fatigue", False))
	irregular_heartbeat = _to_bool(payload.get("irregular_heartbeat", False))

	smoking = _normalize_key(payload.get("smoking", "never"))
	smoking_current = smoking in {"yes", "current", "true", "1"}
	smoking_former = smoking in {"former"}
	diabetes = _to_bool(payload.get("diabetes", False))

	# Derive proxy clinical attributes required by the trained dataset model.
	thalach_estimate = max(85.0, min(202.0, 208.0 - (0.7 * age) - (8.0 if shortness_of_breath else 0.0)))
	oldpeak_estimate = min(
		6.0,
		0.6 + (0.7 if shortness_of_breath else 0.0) + (0.4 if fatigue else 0.0) + (0.4 if irregular_heartbeat else 0.0),
	)
	slope_value = 2 if (shortness_of_breath or fatigue) else 1
	restecg_value = 2 if irregular_heartbeat else 0
	exang_value = 1 if shortness_of_breath else 0
	fbs_value = 1 if diabetes else 0
	ca_value = min(3, int(smoking_current) + int(diabetes) + int(irregular_heartbeat))
	thal_value = 3 if (smoking_current and shortness_of_breath) else 2

	feature_row = {
		"age": age,
		"sex": sex,
		"cp": chest_pain,
		"trestbps": blood_pressure,
		"chol": cholesterol,
		"fbs": fbs_value,
		"restecg": restecg_value,
		"thalach": thalach_estimate,
		"exang": exang_value,
		"oldpeak": oldpeak_estimate,
		"slope": slope_value,
		"ca": ca_value,
		"thal": thal_value,
	}

	features = pd.DataFrame([feature_row], columns=FEATURE_COLUMNS)

	for col in CATEGORICAL_COLUMNS:
		features[col] = pd.to_numeric(features[col], errors="coerce").fillna(0).astype(int)
	for col in NUMERIC_COLUMNS:
		features[col] = pd.to_numeric(features[col], errors="coerce").fillna(0.0)

	context = {
		"shortness_of_breath": shortness_of_breath,
		"fatigue": fatigue,
		"irregular_heartbeat": irregular_heartbeat,
		"smoking_current": smoking_current,
		"smoking_former": smoking_former,
		"diabetes": diabetes,
		"blood_pressure": blood_pressure,
		"cholesterol": cholesterol,
	}

	return features, context


def adjust_probability(base_probability, context):
	adjusted = float(base_probability)
	adjusted += 0.07 if context["diabetes"] else 0.0
	adjusted += 0.06 if context["smoking_current"] else 0.0
	adjusted += 0.03 if context["smoking_former"] else 0.0
	adjusted += 0.05 if context["shortness_of_breath"] else 0.0
	adjusted += 0.04 if context["fatigue"] else 0.0
	adjusted += 0.05 if context["irregular_heartbeat"] else 0.0

	if context["blood_pressure"] >= 140:
		adjusted += 0.04
	if context["cholesterol"] >= 240:
		adjusted += 0.03

	return min(0.99, max(0.01, adjusted))


def classify_risk(probability):
	if probability < 0.35:
		return "Low"
	if probability < 0.70:
		return "Medium"
	return "High"


def generate_recommendations(risk_level, context):
	recommendations = []

	if risk_level == "High":
		recommendations.append("Book a cardiology consultation as soon as possible for a full clinical evaluation.")
		recommendations.append("Track blood pressure daily and seek urgent care for chest pain, severe breathlessness, or fainting.")
	elif risk_level == "Medium":
		recommendations.append("Schedule a preventive health check within the next 2-4 weeks.")
		recommendations.append("Monitor symptoms and blood pressure weekly and discuss trends with a doctor.")
	else:
		recommendations.append("Maintain regular annual checkups and continue heart-healthy habits.")

	if context["smoking_current"]:
		recommendations.append("Start a smoking cessation plan immediately and seek support if needed.")
	if context["diabetes"]:
		recommendations.append("Keep blood glucose under control and follow your diabetes care plan closely.")
	if context["blood_pressure"] >= 140:
		recommendations.append("Reduce sodium intake, improve sleep quality, and follow blood pressure treatment guidance.")
	if context["cholesterol"] >= 240:
		recommendations.append("Adopt a low-saturated-fat diet and request a lipid profile review.")
	if context["shortness_of_breath"] or context["irregular_heartbeat"]:
		recommendations.append("Do not ignore persistent breathing changes or palpitations; seek medical assessment promptly.")

	recommendations.append("This tool is a screening assistant and does not replace professional diagnosis.")
	return recommendations
