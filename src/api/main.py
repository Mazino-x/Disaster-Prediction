import os
import flask
from flask import request, jsonify
import joblib
import pandas as pd
from pathlib import Path
import math
import numpy as np

# Optional CORS is enabled for local development. Add flask-cors to requirements.txt
try:
    from flask_cors import CORS
except Exception:
    CORS = None

app = flask.Flask(__name__)
if CORS:
    CORS(app)

models_dir = Path(__file__).parent / 'models'

# Load models safely at import time. If a model file is missing or fails to load,
# log and keep the variable as None so the API remains importable for tooling
# and simple health checks.
def _safe_load_model(path: Path):
    try:
        if path.exists():
            return joblib.load(path)
        else:
            app.logger.warning(f"Model file not found: {path}")
    except Exception:
        app.logger.exception(f"Failed to load model: {path}")
    return None

earthquake_model = _safe_load_model(models_dir / 'earthquake_model.joblib')
tsunami_model = _safe_load_model(models_dir / 'tsunami_model.joblib')

# Load historical tsunami locations to avoid showing high tsunami risk in places
# with no recorded tsunami history. Prefer a cleaned CSV if available.
project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / 'data'
tsunami_history_file = data_dir / 'tsunami_cleaned.csv'
if not tsunami_history_file.exists():
    tsunami_history_file = data_dir / 'tsunami_historical_data_from_1800_to_2021.csv'

_historical_tsunami_coords = None
try:
    _th = pd.read_csv(tsunami_history_file)
    # Prefer the cleaned label if present, otherwise infer from validity/MWH
    if 'label_tsunami' in _th.columns:
        positives = _th[_th['label_tsunami'] == 1]
    else:
        # fall back to validity >=3 OR MWH>=0.5
        mwh_col = next((c for c in _th.columns if 'maximum water height' in c.lower()), None)
        val_col = next((c for c in _th.columns if c.lower() == 'tsunami event validity'), None)
        cond = pd.Series(False, index=_th.index)
        if val_col:
            cond = cond | (_th[val_col].fillna(-999).astype(float) >= 3)
        if mwh_col:
            cond = cond | (pd.to_numeric(_th[mwh_col], errors='coerce').fillna(0) >= 0.5)
        positives = _th[cond]
    # Collect coordinates and drop NAs
    lat_col = next((c for c in _th.columns if c.lower() == 'latitude'), None)
    lon_col = next((c for c in _th.columns if c.lower() == 'longitude'), None)
    if lat_col and lon_col:
        coords = positives[[lat_col, lon_col]].dropna()
        _historical_tsunami_coords = coords.values.astype(float)
    else:
        _historical_tsunami_coords = np.empty((0,2))
except Exception:
    _historical_tsunami_coords = np.empty((0,2))

# Configurable radius (km) to consider "nearby" historical tsunami events.
# Can be overridden via the environment variable TSUNAMI_HISTORICAL_RADIUS_KM.
# Default 75 km balances avoiding false positives in inland areas while respecting
# established seismic/tsunami zones (verified via radius sweep).
try:
    TSUNAMI_HISTORICAL_RADIUS_KM = float(os.environ.get('TSUNAMI_HISTORICAL_RADIUS_KM', '75.0'))
except Exception:
    TSUNAMI_HISTORICAL_RADIUS_KM = 75.0


def _haversine_km(lat1, lon1, lat2, lon2):
    # Vectorized haversine distance (returns array of distances if lat2/lon2 are arrays)
    # lat/lon in degrees
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = phi2 - phi1
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def _is_near_historical_tsunami(lat, lon, max_km=None):
    """Return True if (lat,lon) is within max_km of any historical tsunami event.

    If max_km is None, the value of TSUNAMI_HISTORICAL_RADIUS_KM is used.
    """
    try:
        if max_km is None:
            max_km = TSUNAMI_HISTORICAL_RADIUS_KM
        coords = _historical_tsunami_coords
        if coords is None or len(coords) == 0:
            return False
        lats = coords[:,0]
        lons = coords[:,1]
        dists = _haversine_km(lat, lon, lats, lons)
        return np.any(dists <= max_km)
    except Exception:
        return False


def _predict(model, data):
    """Helper: model.predict expects a DataFrame; return first element or None on error."""
    try:
        if model is None:
            app.logger.error('Prediction requested but model is not loaded')
            return None
        # Accept either a single-record dict (wrap in list) or a list of records / DataFrame-able structure
        try:
            df = pd.DataFrame(data)
        except ValueError:
            # pandas complains when given a dict of scalars: wrap as single-row list
            df = pd.DataFrame([data])
        
        # Reorder columns to match model's expected feature order if model has feature_names_in_
        if hasattr(model, 'feature_names_in_'):
            expected_order = list(model.feature_names_in_)
            # Build a best-effort mapping from expected feature names to provided columns
            provided = list(df.columns)
            mapping = {}
            for exp in expected_order:
                # exact match
                if exp in provided:
                    mapping[exp] = exp
                    continue
                # case-insensitive exact
                found = None
                for p in provided:
                    if p.lower() == exp.lower():
                        found = p; break
                if found:
                    mapping[exp] = found
                    continue
                # substring matches (either direction)
                for p in provided:
                    if exp.lower() in p.lower() or p.lower() in exp.lower():
                        found = p; break
                if found:
                    mapping[exp] = found
                    continue
                # try simple aliasing: remove punctuation and parentheses
                exp_s = ''.join(ch for ch in exp if ch.isalnum() or ch.isspace()).lower()
                for p in provided:
                    p_s = ''.join(ch for ch in p if ch.isalnum() or ch.isspace()).lower()
                    if exp_s in p_s or p_s in exp_s:
                        found = p; break
                if found:
                    mapping[exp] = found
                    continue
                # not found: will fill with zeros
                mapping[exp] = None

            # construct DataFrame in expected order; fill missing with zeros
            cols = []
            for exp in expected_order:
                src = mapping.get(exp)
                if src is None:
                    # create a zero column
                    df[exp] = 0
                    cols.append(exp)
                else:
                    cols.append(src)
            # reindex/rename so columns exactly match expected names (models may expect those names)
            df = df[cols].copy()
            # if any src names differ from expected, rename
            rename_map = {v: k for k, v in mapping.items() if v is not None and v != k}
            if rename_map:
                df = df.rename(columns=rename_map)
        
        pred = model.predict(df)
        # Convert numpy types to Python native types for JSON serialization
        result = pred[0]
        if hasattr(result, 'item'):
            result = result.item()
        return result
    except Exception as e:
        # Keep payload errors visible in logs and return a 400-ish JSON response
        app.logger.exception('Prediction error')
        return None


# Earthquake Prediction
@app.route('/earthquake', methods=['POST'])
def earthquake():
    data = request.get_json()
    prediction = _predict(earthquake_model, data)
    if prediction is None:
        return jsonify({'error': 'invalid payload or prediction failed'}), 400
    return jsonify({'prediction': prediction})



@app.route('/tsunami', methods=['POST'])
def tsunami():
    data = request.get_json()
    # Use existing _predict to get model prediction
    prediction = _predict(tsunami_model, data)
    if prediction is None:
        return jsonify({'error': 'invalid payload or prediction failed'}), 400

    # If model predicts a tsunami, but location has no historical tsunamis nearby,
    # override to LOW RISK. Extract latitude/longitude from payload keys if available.
    try:
        lat = None
        lon = None
        if isinstance(data, dict):
            for k, v in data.items():
                kl = k.lower()
                if 'lat' == kl or kl.endswith('latitude') or 'latitude' in kl:
                    try:
                        lat = float(v)
                    except Exception:
                        pass
                if 'lon' == kl or kl.endswith('longitude') or 'longitude' in kl:
                    try:
                        lon = float(v)
                    except Exception:
                        pass
        # fallback to look for keys case-insensitively
        if lat is None or lon is None:
            for k in data.keys():
                kl = k.lower()
                if 'lat' in kl and lat is None:
                    try: lat = float(data[k]);
                    except: pass
                if 'lon' in kl and lon is None:
                    try: lon = float(data[k]);
                    except: pass
    except Exception:
        lat = lon = None

    if prediction == 1:
        if lat is not None and lon is not None:
            nearby = _is_near_historical_tsunami(lat, lon)
            if not nearby:
                # override prediction
                return jsonify({'prediction': 0, 'note': f'overrode positive because no historical tsunami within {TSUNAMI_HISTORICAL_RADIUS_KM} km'} )
        else:
            # no coordinates provided - conservatively keep prediction
            pass

    return jsonify({'prediction': prediction})


# Main
if __name__ == '__main__':
    # Bind explicitly and disable the auto-reloader to avoid duplicate processes
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)


    