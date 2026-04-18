import React, { useState, useContext } from 'react';
import './EarthquakePrediction.css'; // shared styles
import { PredictionContext } from './PredictionContext';
import REGIONS from './regions';

// BUG FIX: text inputs changed to type="number"; validation extended
// BUG FIX: result was stored in context but never displayed — now rendered
// BUG FIX: depth field was collected but not sent in payload — now included

const BACKEND = process.env.REACT_APP_API_URL || 'https://disaster-prediction-backend-yrcl.onrender.com';

function TsunamiPrediction() {
  const [region,    setRegion]    = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [latitude,  setLatitude]  = useState('');
  const [longitude, setLongitude] = useState('');
  const [depth,     setDepth]     = useState('');
  const [magnitude, setMagnitude] = useState('');
  const [date,      setDate]      = useState('');
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [result,    setResult]    = useState(null);
  const { addPrediction }         = useContext(PredictionContext);

  const selectedRegion = REGIONS.find(r => r.value === region);
  const filteredRegions = searchTerm
    ? REGIONS.filter(item => item.label.toLowerCase().includes(searchTerm.toLowerCase()))
    : [];

  const handleRegionSelect = (item) => {
    setRegion(item.value);
    setSearchTerm(item.label);
    setLatitude(item.latitude.toString());
    setLongitude(item.longitude.toString());
    setError(null);
  };

  const validate = () => {
    const lat = selectedRegion ? selectedRegion.latitude : parseFloat(latitude);
    const lon = selectedRegion ? selectedRegion.longitude : parseFloat(longitude);
    if ((!selectedRegion && (!latitude || !longitude)) || !depth || !magnitude || !date) return 'Please fill in all fields.';
    if (isNaN(lat) || lat < -90  || lat > 90)  return 'Latitude must be between -90 and 90.';
    if (isNaN(lon) || lon < -180 || lon > 180) return 'Longitude must be between -180 and 180.';
    if (isNaN(parseFloat(depth)) || parseFloat(depth) < 0) return 'Depth must be a positive number.';
    if (isNaN(parseFloat(magnitude)) || parseFloat(magnitude) < 0 || parseFloat(magnitude) > 10) return 'Magnitude must be between 0 and 10.';
    return null;
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) { setError(validationError); return; }

    setLoading(true);
    setError(null);
    setResult(null);

    const d = new Date(date);
    const lat = selectedRegion ? selectedRegion.latitude : parseFloat(latitude);
    const lon = selectedRegion ? selectedRegion.longitude : parseFloat(longitude);
    const payload = {
      Latitude:  lat,
      Longitude: lon,
      Depth:     parseFloat(depth),
      'Tsunami Magnitude (Iida)': parseFloat(magnitude),
      Year: d.getFullYear(),
      Mo:   d.getMonth() + 1,
      Dy:   d.getDate(),
      Hr: 12, Mn: 0, Sec: 0,
    };

    try {
      const res  = await fetch(`${BACKEND}/tsunami`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      if (res.ok) {
        setResult({ value: json.prediction, probability: json.probability });
        addPrediction('Tsunami', { latitude, longitude, depth, magnitude, date }, json.prediction, json.probability);
      } else {
        setError(json.error || 'Prediction failed. Check backend connection.');
      }
    } catch (err) {
      setError('Cannot reach the backend. Make sure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const isHighRisk = result?.value === 1;
  const isLowRisk  = result?.value === 0;
  const probabilityText = result?.probability != null
    ? `Confidence: ${(result.probability * 100).toFixed(1)}%`
    : null;

  return (
    <div className="predictionPage">
      <div className="pageHeader">
        <span className="pageIcon">🌊</span>
        <div>
          <h1>Tsunami Prediction</h1>
          <p>Enter seismic parameters to assess tsunami risk</p>
        </div>
      </div>

      <div className="formCard">
        <div className="formGrid">
            <div className="fieldGroup">
              <label htmlFor="ts-region-search">Search region or city</label>
              <input
                type="text"
                id="ts-region-search"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setRegion('');
                }}
                placeholder="e.g. Australia, Canada, Tokyo"
                autoComplete="off"
              />
              {searchTerm && filteredRegions.length > 0 && (
                <div className="regionSuggestions">
                  {filteredRegions.slice(0, 8).map(item => (
                    <button
                      key={item.value}
                      type="button"
                      className="regionSuggestion"
                      onClick={() => handleRegionSelect(item)}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="fieldGroup">
              <label htmlFor="ts-lat">Latitude <span className="hint">−90 to 90</span></label>
              <input
                type="number" id="ts-lat" step="0.0001" min="-90" max="90"
                value={latitude} onChange={e => {
                  setRegion('');
                  setSearchTerm('');
                  setLatitude(e.target.value);
                }}
                placeholder="e.g. 35.6762"
                disabled={Boolean(region)}
              />
            </div>
            <div className="fieldGroup">
              <label htmlFor="ts-lon">Longitude <span className="hint">−180 to 180</span></label>
              <input
                type="number" id="ts-lon" step="0.0001" min="-180" max="180"
                value={longitude} onChange={e => {
                  setRegion('');
                  setSearchTerm('');
                  setLongitude(e.target.value);
                }}
                placeholder="e.g. 139.6503"
                disabled={Boolean(region)}
              />
            </div>
            <div className="fieldGroup">
              <label htmlFor="ts-depth">Depth (km) <span className="hint">positive number</span></label>
              <input
                type="number" id="ts-depth" step="0.1" min="0"
                value={depth} onChange={e => setDepth(e.target.value)}
                placeholder="e.g. 10"
              />
            </div>
            <div className="fieldGroup">
              <label htmlFor="ts-mag">Magnitude (Iida) <span className="hint">0 – 10</span></label>
              <input
                type="number" id="ts-mag" step="0.1" min="0" max="10"
                value={magnitude} onChange={e => setMagnitude(e.target.value)}
                placeholder="e.g. 6.5"
              />
            </div>
            <div className="fieldGroup">
              <label htmlFor="ts-date">Date</label>
              <input
                type="date" id="ts-date"
                value={date} onChange={e => setDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>
        {error && <div className="alertError">⚠ {error}</div>}

        <button className="submitBtn" onClick={handleSubmit} disabled={loading}>
          {loading ? <><span className="btnSpinner" /> Analysing...</> : 'Predict Risk'}
        </button>
      </div>

      {result !== null && (
        <div className={`resultCard ${isHighRisk ? 'resultHigh' : isLowRisk ? 'resultLow' : 'resultUnknown'}`}>
          <div className="resultIcon">{isHighRisk ? '⚠️' : isLowRisk ? '✅' : '❓'}</div>
          <div className="resultBody">
            <p className="resultLabel">Tsunami Risk</p>
            <p className="resultLevel">{isHighRisk ? 'HIGH RISK' : isLowRisk ? 'LOW RISK' : 'UNKNOWN'}</p>
            {probabilityText && <p className="resultProbability">{probabilityText}</p>}
            <p className="resultDetail">
              {isHighRisk && 'Elevated probability of a tsunami event given these seismic parameters.'}
              {isLowRisk  && 'Low probability of a tsunami event based on historical patterns.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default TsunamiPrediction;
