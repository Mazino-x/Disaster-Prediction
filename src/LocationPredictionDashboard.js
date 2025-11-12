import React, { useState, useContext, useEffect } from 'react';
import { PredictionContext } from './PredictionContext';
import './LocationPredictionDashboard.css';

function LocationPredictionDashboard({ latitude, longitude, locationName, onBack }) {
    const [earthquake, setEarthquake] = useState(null);
    const [tsunami, setTsunami] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { addPrediction } = useContext(PredictionContext);

    useEffect(() => {
        const fetchPredictions = async () => {
            setLoading(true);
            setError(null);
            try {
                // Get current date/time for earthquake prediction
                const now = new Date();
                const year = now.getFullYear();
                const month = now.getMonth() + 1;
                const day = now.getDate();
                const hour = now.getHours();
                const minute = now.getMinutes();
                const second = now.getSeconds();

                const backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';

                // Fetch Earthquake prediction
                try {
                    const eqResponse = await fetch(`${backend}/earthquake`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            Latitude: latitude,
                            Longitude: longitude,
                            Depth: 10,  // typical crustal depth (km)
                            Year: year,
                            Month: month,
                            Day: day,
                            Hour: hour,
                            Minute: minute,
                            Second: second
                        })
                    });
                    const eqData = await eqResponse.json();
                    setEarthquake(eqData.prediction);
                } catch (e) {
                    console.error('Earthquake prediction failed:', e);
                    setEarthquake('Error');
                }

                // Fetch Tsunami prediction
                // Note: Tsunami model expects abbreviated field names (Mo, Dy, Hr, Mn, Sec)
                try {
                    const tsunamiResponse = await fetch(`${backend}/tsunami`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            Latitude: latitude,
                            Longitude: longitude,
                            'Tsunami Magnitude (Iida)': 6.5,  // typical tsunami magnitude
                            Year: year,
                            Mo: month,  // abbreviated field name
                            Dy: day,    // abbreviated field name
                            Hr: hour,   // abbreviated field name
                            Mn: minute, // abbreviated field name
                            Sec: second // abbreviated field name
                        })
                    });
                    const tsunamiData = await tsunamiResponse.json();
                    setTsunami(tsunamiData.prediction);
                } catch (e) {
                    console.error('Tsunami prediction failed:', e);
                    setTsunami('Error');
                }
            } catch (e) {
                setError('Failed to fetch predictions: ' + e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchPredictions();
    }, [latitude, longitude]);

    const getRiskLevel = (prediction) => {
        if (prediction === 'Error' || prediction === null) return 'Unknown';
        if (prediction === 0) return 'LOW RISK';
        if (prediction === 1) return 'HIGH RISK';
        return 'Unknown';
    };

    const getRiskColor = (prediction) => {
        if (prediction === 'Error' || prediction === null) return '#95a5a6';
        if (prediction === 0) return '#27ae60';
        if (prediction === 1) return '#e74c3c';
        return '#95a5a6';
    };

    const getRiskEmoji = (prediction) => {
        if (prediction === 'Error' || prediction === null) return '?';
        if (prediction === 0) return '✓';
        if (prediction === 1) return '⚠';
        return '?';
    };

    if (loading) {
        return (
            <div className="dashboardContainer">
                <div className="loadingBox">
                    <div className="spinner"></div>
                    <p>Fetching disaster predictions...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboardContainer">
            <div className="dashboardHeader">
                <button className="backBtn" onClick={onBack}>← Back to Map</button>
                <h1>Disaster Risk Assessment</h1>
                <p className="locationInfo">{locationName}</p>
                <p className="coordinates">Latitude: {latitude.toFixed(4)} | Longitude: {longitude.toFixed(4)}</p>
            </div>

            {error && <div className="errorBox">{error}</div>}

            <div className="predictionsGrid">
                <div className="predictionCard earthquakeCard">
                    <h2>🌍 Earthquake Risk</h2>
                    <div className="predictionValue">
                        <div
                            className="riskIndicator"
                            style={{ backgroundColor: getRiskColor(earthquake) }}
                        >
                            {getRiskEmoji(earthquake)}
                        </div>
                        <div className="riskText">
                            <p className="riskLevel">{getRiskLevel(earthquake)}</p>
                            <p className="riskDetail">
                                {earthquake === 0 && 'Low probability of seismic activity'}
                                {earthquake === 1 && 'High probability of seismic activity'}
                                {earthquake === 'Error' && 'Assessment unavailable'}
                            </p>
                        </div>
                    </div>
                    <div className="cardDetails">
                        <p><strong>Location:</strong> {latitude.toFixed(4)}°, {longitude.toFixed(4)}°</p>
                        <p><strong>Depth:</strong> 10 km (assumed crustal)</p>
                        <p><strong>Model Confidence:</strong> ~75.5%</p>
                        <p><strong>Assessment:</strong> {new Date().toLocaleString()}</p>
                    </div>
                </div>

                {/* Flood card removed per request */}

                <div className="predictionCard tsunamiCard">
                    <h2>🌊 Tsunami Risk</h2>
                    <div className="predictionValue">
                        <div
                            className="riskIndicator"
                            style={{ backgroundColor: getRiskColor(tsunami) }}
                        >
                            {getRiskEmoji(tsunami)}
                        </div>
                        <div className="riskText">
                            <p className="riskLevel">{getRiskLevel(tsunami)}</p>
                            <p className="riskDetail">
                                {tsunami === 0 && 'Low probability of tsunami events'}
                                {tsunami === 1 && 'High probability of tsunami events'}
                                {tsunami === 'Error' && 'Assessment unavailable'}
                            </p>
                        </div>
                    </div>
                    <div className="cardDetails">
                        <p><strong>Location:</strong> {latitude.toFixed(4)}°, {longitude.toFixed(4)}°</p>
                        <p><strong>Reference Magnitude:</strong> 6.5 (typical for assessment)</p>
                        <p><strong>Model Confidence:</strong> ~77.0%</p>
                        <p><strong>Assessment:</strong> {new Date().toLocaleString()}</p>
                    </div>
                </div>
            </div>

            <div className="assessmentFooter">
                <p>
                    <strong>Important Disclaimer:</strong> These predictions are based on machine learning models trained on historical seismic and tsunami data. 
                    <br/>
                    <strong>Limitations:</strong>
                    <ul>
                        <li>Risk assessment uses simplified assumptions (depth: 10 km, earthquake magnitude varies)</li>
                        <li>Models are trained on historical patterns and may not predict unprecedented events</li>
                        <li>Actual risk depends on many factors including local geology, infrastructure, and population density</li>
                        <li>DO NOT rely solely on these predictions for life-safety decisions</li>
                    </ul>
                    <strong>For Official Information:</strong> Consult your local seismic monitoring agency, USGS (USA), JMA (Japan), or other official government disaster warning systems.
                </p>
            </div>
        </div>
    );
}

export default LocationPredictionDashboard;
