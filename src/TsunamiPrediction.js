import React, { useState, useContext } from 'react';
import './TsunamiPrediction.css';
import { PredictionContext } from './PredictionContext';

function TsunamiPrediction() {
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [depth, setDepth] = useState('');
    const [magnitude, setMagnitude] = useState('');
    const [date, setDate] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { addPrediction } = useContext(PredictionContext);
    const backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';

    const handleSubmit = async () => {
        if (!latitude || !longitude || !depth || !magnitude || !date) {
            setError('Please fill all fields');
            return;
        }

        setLoading(true);
        setError(null);
        
        // Extract components from date for model features
        const dateObj = new Date(date);
        // Model expects: ['Latitude' 'Longitude' 'Tsunami Magnitude (Iida)' 'Year' 'Mo' 'Dy' 'Hr' 'Mn' 'Sec']
        const payload = {
            Latitude: parseFloat(latitude),
            Longitude: parseFloat(longitude),
            'Tsunami Magnitude (Iida)': parseFloat(magnitude),
            Year: dateObj.getFullYear(),
            Mo: dateObj.getMonth() + 1,
            Dy: dateObj.getDate(),
            Hr: 12,  // Default hour
            Mn: 0,   // Default minute
            Sec: 0   // Default second
        };

        try {
            const res = await fetch(`${backend}/tsunami`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (res.ok) {
                addPrediction('Tsunami', { latitude, longitude, depth, magnitude, date }, json.prediction);
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
                <h2>Tsunami Prediction</h2>
            </div>
            <div className="manualCoordinatesContainer">
                <h3 className="manualCoordinatesHeading">Enter tsunami parameters:</h3>
                <div className="manualCoordinatesForm">
                <label htmlFor="latitude">Latitude:</label>
                    <input type="text" id="latitude" name="latitude" value={latitude} onChange={e => setLatitude(e.target.value)} placeholder="e.g., 12.34" />

                    <label htmlFor="longitude">Longitude:</label>
                    <input type="text" id="longitude" name="longitude" value={longitude} onChange={e => setLongitude(e.target.value)} placeholder="e.g., 56.78" />

                    <label htmlFor="depth">Depth (km):</label>
                    <input type="text" id="depth" name="depth" value={depth} onChange={e => setDepth(e.target.value)} placeholder="e.g., 10" />

                    <label htmlFor="magnitude">Magnitude:</label>
                    <input type="text" id="magnitude" name="magnitude" value={magnitude} onChange={e => setMagnitude(e.target.value)} placeholder="e.g., 6.5" />

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

export default TsunamiPrediction;