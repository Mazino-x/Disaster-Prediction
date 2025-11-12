import React, { useContext } from 'react';
import './PredictionHistory.css';
import { PredictionContext } from './PredictionContext';

function PredictionHistory() {
    const { predictions, clearPredictions } = useContext(PredictionContext);

    return (
        <div className="predictionHistoryContainer">
            <div className="historyHeader">
                <h2>Prediction History</h2>
                {predictions.length > 0 && (
                    <button onClick={clearPredictions} className="clearBtn">Clear</button>
                )}
            </div>
            {predictions.length === 0 ? (
                <p className="noData">No predictions yet. Use the forms above to make predictions.</p>
            ) : (
                <div className="historyList">
                    {predictions.map(pred => (
                        <div key={pred.id} className="historyItem">
                            <div className="itemHeader">
                                <span className="type">{pred.type}</span>
                                <span className="timestamp">{pred.timestamp}</span>
                            </div>
                            <div className="itemInputs">
                                <strong>Input:</strong>
                                <pre>{JSON.stringify(pred.inputs, null, 2)}</pre>
                            </div>
                            <div className="itemResult">
                                <strong>Result:</strong>
                                <span className="resultValue">{String(pred.result)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default PredictionHistory;
