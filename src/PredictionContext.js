import React, { createContext, useState, useCallback } from 'react';

export const PredictionContext = createContext();

export function PredictionProvider({ children }) {
    const [predictions, setPredictions] = useState([]);

    const addPrediction = useCallback((type, inputs, result) => {
        const timestamp = new Date().toLocaleTimeString();
        setPredictions(prev => [
            ...prev,
            { id: Date.now(), type, inputs, result, timestamp }
        ]);
    }, []);

    const clearPredictions = useCallback(() => {
        setPredictions([]);
    }, []);

    return (
        <PredictionContext.Provider value={{ predictions, addPrediction, clearPredictions }}>
            {children}
        </PredictionContext.Provider>
    );
}
