"""
Disaster Prediction API
-----------------------
Flask backend serving earthquake and tsunami risk predictions.

FIXES applied vs original:
  - Removed duplicate lat/lon extraction loop in /tsunami route
  - Added /health endpoint for readiness checks
  - Consistent JSON error shapes (always {error: str})
  - Input validation at route level (400 on clearly bad payloads)
  - Added CORS headers even when flask-cors is absent (simple manual header)
  - Model-load failures now logged with exc_info for actionable tracebacks
  - Moved TSUNAMI_HISTORICAL_RADIUS_KM parse into a helper to avoid bare except
"""

import os
import math
import logging

import flask
from flask import request, jsonify
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

try:
    from flask_cors import CORS
    _has_flask_cors = True
except ImportError:
    _has_flask_cors = False

# ── App setup ────────────────────────────────────────────────────────────────
app = flask.Flask(__name__)
logging.basicConfig(level=logging.INFO)

if _has_flask_cors:
    CORS(app)
else:
    # Manual CORS fallback so the React dev server can reach us without flask-cors
    @app.after_request
    def _add_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.route("/earthquake", methods=["OPTIONS"])
    @app.route("/tsunami", methods=["OPTIONS"])
    @app.route("/health", methods=["OPTIONS"])
    def _preflight():
        return "", 204


# ── Model loading ─────────────────────────────────────────────────────────────
models_dir = Path(__file__).parent / "models"


def _safe_load_model(path: Path):
    if not path.exists():
        app.logger.warning("Model file not found: %s", path)
        return None
    try:
        model = joblib.load(path)
        app.logger.info("Loaded model: %s", path.name)
        return model
    except Exception:
        app.logger.exception("Failed to load model: %s", path)
        return None


earthquake_model = _safe_load_model(models_dir / "earthquake_model.joblib")
tsunami_model    = _safe_load_model(models_dir / "tsunami_model.joblib")


def _reload_models():
    global earthquake_model, tsunami_model, _historical_tsunami_coords, _historical_tsunami_path
    earthquake_model = _safe_load_model(models_dir / "earthquake_model.joblib")
    tsunami_model = _safe_load_model(models_dir / "tsunami_model.joblib")
    _historical_tsunami_coords, _historical_tsunami_path = _load_tsunami_history()
    return {
        "earthquake": earthquake_model is not None,
        "tsunami": tsunami_model is not None,
        "historical_tsunami_coords": len(_historical_tsunami_coords),
        "historical_tsunami_path": str(_historical_tsunami_path) if _historical_tsunami_path else None,
    }


# ── Historical tsunami coordinates ────────────────────────────────────────────
project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / "data"

def _load_tsunami_history():
    for fname in ("tsunami_cleaned.csv", "tsunami_historical_data_from_1800_to_2021.csv"):
        path = data_dir / fname
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
            if "label_tsunami" in df.columns:
                positives = df[df["label_tsunami"] == 1]
            else:
                mwh_col = next((c for c in df.columns if "maximum water height" in c.lower()), None)
                val_col = next((c for c in df.columns if c.lower() == "tsunami event validity"), None)
                cond = pd.Series(False, index=df.index)
                if val_col:
                    cond |= df[val_col].fillna(-999).astype(float) >= 3
                if mwh_col:
                    cond |= pd.to_numeric(df[mwh_col], errors="coerce").fillna(0) >= 0.5
                positives = df[cond]

            lat_col = next((c for c in df.columns if c.lower() == "latitude"), None)
            lon_col = next((c for c in df.columns if c.lower() == "longitude"), None)
            if lat_col and lon_col:
                coords = positives[[lat_col, lon_col]].dropna().values.astype(float)
                app.logger.info("Loaded %d historical tsunami coords from %s", len(coords), fname)
                return coords, path
        except Exception:
            app.logger.exception("Failed to load tsunami history from %s", path)
    return np.empty((0, 2)), None


_historical_tsunami_coords, _historical_tsunami_path = _load_tsunami_history()

def _get_radius_km() -> float:
    try:
        return float(os.environ.get("TSUNAMI_HISTORICAL_RADIUS_KM", "75.0"))
    except (TypeError, ValueError):
        return 75.0

TSUNAMI_HISTORICAL_RADIUS_KM = _get_radius_km()


# ── Haversine ─────────────────────────────────────────────────────────────────
def _haversine_km(lat1: float, lon1: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = np.radians(lats)
    dphi = phi2 - phi1
    dlambda = np.radians(lons - lon1)
    a = np.sin(dphi / 2) ** 2 + math.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def _is_near_historical_tsunami(lat: float, lon: float, max_km: float = None) -> bool:
    if max_km is None:
        max_km = TSUNAMI_HISTORICAL_RADIUS_KM
    coords = _historical_tsunami_coords
    if coords is None or len(coords) == 0:
        # No historical tsunami coordinate data available.
        # In this case, do not suppress a model high-risk prediction.
        return True
    try:
        dists = _haversine_km(lat, lon, coords[:, 0], coords[:, 1])
        return bool(np.any(dists <= max_km))
    except Exception:
        return False


# ── Prediction helper ─────────────────────────────────────────────────────────
def _predict(model, data: dict, use_threshold: float = None):
    """Run model.predict on a single-row dict; return native Python value or None.
    
    Args:
        model: sklearn pipeline model
        data: feature dict
        use_threshold: optional custom decision threshold (for probability-based predictions)
    """
    if model is None:
        app.logger.error("Prediction requested but model is not loaded")
        return None
    try:
        # Build DataFrame, wrap scalar dict in list
        try:
            df = pd.DataFrame(data)
        except ValueError:
            df = pd.DataFrame([data])

        # Re-order / rename columns to match model's expected feature names
        if hasattr(model, "feature_names_in_"):
            expected = list(model.feature_names_in_)
            provided = list(df.columns)

            def _best_match(exp, candidates):
                # 1. exact
                if exp in candidates:
                    return exp
                # 2. case-insensitive
                el = exp.lower()
                for c in candidates:
                    if c.lower() == el:
                        return c
                # 3. substring either direction
                for c in candidates:
                    cl = c.lower()
                    if el in cl or cl in el:
                        return c
                # 4. alphanumeric-only comparison
                exp_s = "".join(ch for ch in exp if ch.isalnum()).lower()
                for c in candidates:
                    c_s = "".join(ch for ch in c if ch.isalnum()).lower()
                    if exp_s in c_s or c_s in exp_s:
                        return c
                return None

            mapping = {exp: _best_match(exp, provided) for exp in expected}

            # Fill missing columns with zeros, reorder
            for exp, src in mapping.items():
                if src is None:
                    df[exp] = 0

            cols = [mapping[exp] if mapping[exp] is not None else exp for exp in expected]
            df = df[cols].copy()
            rename = {v: k for k, v in mapping.items() if v is not None and v != k}
            if rename:
                df = df.rename(columns=rename)

        probability = None
        if use_threshold is not None:
            try:
                proba = model.predict_proba(df)
                probability = float(proba[:, 1][0])
                result = (proba[:, 1] >= use_threshold).astype(int)[0]
            except Exception:
                # Fall back to standard predict
                pred = model.predict(df)
                result = pred[0]
        else:
            pred = model.predict(df)
            result = pred[0]
            try:
                proba = model.predict_proba(df)
                probability = float(proba[:, 1][0])
            except Exception:
                probability = None

        final_result = result.item() if hasattr(result, "item") else result
        return {"prediction": final_result, "probability": probability}

    except Exception:
        app.logger.exception("Prediction error")
        return None


# ── Extract lat/lon from a payload dict ───────────────────────────────────────
def _extract_lat_lon(data: dict):
    """Return (lat, lon) floats from payload or (None, None) if not found."""
    lat = lon = None
    for k, v in data.items():
        kl = k.lower()
        if lat is None and ("latitude" in kl or kl == "lat"):
            try:
                lat = float(v)
            except (TypeError, ValueError):
                pass
        if lon is None and ("longitude" in kl or kl == "lon"):
            try:
                lon = float(v)
            except (TypeError, ValueError):
                pass
    return lat, lon


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "models": {
            "earthquake": earthquake_model is not None,
            "tsunami":    tsunami_model is not None,
        },
        "model_paths": {
            "earthquake": str(models_dir / "earthquake_model.joblib"),
            "tsunami": str(models_dir / "tsunami_model.joblib"),
        },
        "historical_tsunami_coords": len(_historical_tsunami_coords),
        "historical_tsunami_data_path": str(_historical_tsunami_path) if _historical_tsunami_path else None,
    })


@app.route("/reload", methods=["POST"])
def reload_models():
    status = _reload_models()
    return jsonify({"status": "reloaded", **status})


@app.route("/earthquake", methods=["POST"])
def earthquake():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # If map-based frontend omits depth, assume a shallow crustal earthquake depth.
    earthquake_data = dict(data)
    if not any(k.lower() == "depth" for k in earthquake_data):
        earthquake_data["Depth"] = 10.0
    else:
        # Normalize missing or invalid depth values.
        for k in list(earthquake_data):
            if k.lower() == "depth":
                try:
                    earthquake_data[k] = float(earthquake_data[k])
                except (TypeError, ValueError):
                    earthquake_data[k] = 10.0
                break

    # Fill missing time fields if the frontend does not provide them.
    from datetime import datetime
    now = datetime.utcnow()
    defaults = {
        "Year": now.year,
        "Month": now.month,
        "Day": now.day,
        "Hour": now.hour,
        "Minute": now.minute,
        "Second": now.second,
    }
    for field, value in defaults.items():
        if not any(k.lower() == field.lower() for k in earthquake_data):
            earthquake_data[field] = value

    prediction = _predict(earthquake_model, earthquake_data)
    if prediction is None:
        return jsonify({"error": "Prediction failed — check server logs"}), 400

    return jsonify({
        "prediction": prediction["prediction"],
        "probability": prediction["probability"],
    })


@app.route("/tsunami", methods=["POST"])
def tsunami():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Use a slightly stricter threshold to reduce overprediction of rare tsunami events.
    prediction = _predict(tsunami_model, data, use_threshold=0.90)
    if prediction is None:
        return jsonify({"error": "Prediction failed — check server logs"}), 400

    prediction_value = prediction["prediction"]
    probability = prediction["probability"]
    lat, lon = _extract_lat_lon(data)
    if prediction_value == 1 and lat is not None and lon is not None:
        if not _is_near_historical_tsunami(lat, lon):
            app.logger.info(
                "Suppressing tsunami high prediction because location is not near historical tsunami events: %s,%s",
                lat,
                lon,
            )
            prediction_value = 0

    return jsonify({
        "prediction": prediction_value,
        "probability": probability,
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
