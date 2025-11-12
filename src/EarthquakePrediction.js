import React, { useState, useContext } from 'react';
import './EarthquakePrediction.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { PredictionContext } from './PredictionContext';

const position = [51.505, -0.09];

function EarthquakePrediction() {
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [depth, setDepth] = useState('');
    const [date, setDate] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { addPrediction } = useContext(PredictionContext);
    const backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';

    const handleSubmit = async () => {
        if (!latitude || !longitude || !depth || !date) {
            setError('Please fill all fields');
            return;
        }

        setLoading(true);
        setError(null);
        
        // Extract components from date for model features
        const dateObj = new Date(date);
        // Model expects in this order: ['Latitude' 'Longitude' 'Depth' 'Year' 'Month' 'Day' 'Hour' 'Minute' 'Second']
        const payload = {
            Latitude: parseFloat(latitude),
            Longitude: parseFloat(longitude),
            Depth: parseFloat(depth),
            Year: dateObj.getFullYear(),
            Month: dateObj.getMonth() + 1,
            Day: dateObj.getDate(),
            Hour: 12,
            Minute: 0,
            Second: 0
        };

        try {
            const res = await fetch(`${backend}/earthquake`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (res.ok) {
                addPrediction('Earthquake', { latitude, longitude, depth, date }, json.prediction);
            } else {
                setError(json.error || 'Prediction failed');
            }
        } catch (err) {
            console.error('Error calling backend', err);
            setError('Connection error. Is the backend running on localhost:5000?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="headingContainer">
                <h2>Earthquake Prediction</h2>
            </div>
            <div className="manualCoordinatesContainer">
                <h3 className="manualCoordinatesHeading">Enter earthquake parameters</h3>
                <div className="manualCoordinatesForm">
                    <label htmlFor="latitude">Latitude:</label>
                    <input type="text" id="latitude" name="latitude" value={latitude} onChange={e => setLatitude(e.target.value)} placeholder="e.g., 12.34" />

                    <label htmlFor="longitude">Longitude:</label>
                    <input type="text" id="longitude" name="longitude" value={longitude} onChange={e => setLongitude(e.target.value)} placeholder="e.g., 56.78" />

                    <label htmlFor="depth">Depth (km):</label>
                    <input type="text" id="depth" name="depth" value={depth} onChange={e => setDepth(e.target.value)} placeholder="e.g., 10" />

                    <label htmlFor='date'>Date:</label>
                    <input type='date' id='date' name='date' value={date} onChange={e => setDate(e.target.value)} />

                    <button onClick={handleSubmit} disabled={loading}>
                        {loading ? 'Predicting...' : 'Predict'}
                    </button>
                </div>
                {error && <div className="errorMessage">{error}</div>}
            </div>
        </div>
    );
}

export default EarthquakePrediction;