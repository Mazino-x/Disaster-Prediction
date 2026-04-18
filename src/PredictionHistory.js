import React, { useContext } from 'react';
import './PredictionHistory.css';
import { PredictionContext } from './PredictionContext';

// BUG FIX: raw 0/1 prediction was displayed as-is — now rendered as LOW/HIGH RISK
// IMPROVEMENT: shows colour-coded badge per risk level

const RISK_LABEL = { 0: 'LOW RISK', 1: 'HIGH RISK' };
const RISK_CLASS = { 0: 'riskLow', 1: 'riskHigh' };

const INPUT_LABELS = {
  latitude: 'Latitude', longitude: 'Longitude',
  depth: 'Depth (km)', magnitude: 'Magnitude', date: 'Date',
};

function PredictionHistory() {
  const { predictions, clearPredictions } = useContext(PredictionContext);

  return (
    <div className="historySection">
      <div className="historyTopBar">
        <h2>Prediction History</h2>
        {predictions.length > 0 && (
          <button onClick={clearPredictions} className="clearHistoryBtn">Clear all</button>
        )}
      </div>

      {predictions.length === 0 ? (
        <p className="historyEmpty">No predictions yet — results will appear here after you submit a form above.</p>
      ) : (
        <div className="historyList">
          {[...predictions].reverse().map(pred => (
            <div key={pred.id} className="historyItem">
              <div className="historyItemTop">
                <span className={`typeBadge type${pred.type}`}>{pred.type}</span>
                <span className="historyTime">{pred.timestamp}</span>
                <span className={`riskBadge ${RISK_CLASS[pred.result] || 'riskUnknown'}`}>
                  {RISK_LABEL[pred.result] ?? 'UNKNOWN'}
                </span>
                {pred.probability != null && (
                  <span className="historyProbability">
                    {`${(pred.probability * 100).toFixed(1)}%`}
                  </span>
                )}
                {pred.probability != null && (
                  <span className="historyProbability">
                    {`${(pred.probability * 100).toFixed(1)}%`}
                  </span>
                )}
              </div>
              <div className="historyParams">
                {Object.entries(pred.inputs).map(([k, v]) => (
                  <div key={k} className="paramChip">
                    <span className="paramKey">{INPUT_LABELS[k] || k}</span>
                    <span className="paramVal">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PredictionHistory;

