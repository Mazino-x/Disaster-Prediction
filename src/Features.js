import './Features.css';

function Features() {
    return (
        <div className="featuresContainer">
            {/* Redirect to new page when clicking on these feature cards */}
            <div className="feature featureLocation" onClick={() => window.location.href = '/location'}>
                <h3 className="featureName">Location-Based Risk Assessment</h3>
            </div>
            <div className="feature feature1" onClick={() => window.location.href = '/earthquake'}>
                <h3 className="featureName">Earthquake Prediction</h3>
            </div>
            <div className="feature feature3" onClick={() => window.location.href = '/tsunami'}>
                <h3 className="featureName">Tsunami Prediction</h3>
            </div>
            {/* Flood feature removed per request */}
        </div>
    );
}

export default Features;