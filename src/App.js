import './App.css';
import Front from './Front';
import EarthquakePrediction from './EarthquakePrediction';
import TsunamiPrediction from './TsunamiPrediction';
import LocationSearch from './LocationSearch';
import LocationPredictionDashboard from './LocationPredictionDashboard';
import PredictionHistory from './PredictionHistory';
import { PredictionProvider } from './PredictionContext';
import { BrowserRouter, Route, Routes, useNavigate } from "react-router-dom";
import { useState } from 'react';

function AppRoutes() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const navigate = useNavigate();

  const handleLocationSelected = (lat, lng, name) => {
    setSelectedLocation({ latitude: lat, longitude: lng, name });
    navigate('/predictions');
  };

  const handleBackToMap = () => {
    setSelectedLocation(null);
    navigate('/location');
  };

  return (
    <Routes>
      <Route path='/' element={<Front />} />
      <Route path="/location" element={<LocationSearch onLocationSelected={handleLocationSelected} />} />
      <Route 
        path="/predictions" 
        element={
          selectedLocation ? (
            <LocationPredictionDashboard 
              latitude={selectedLocation.latitude}
              longitude={selectedLocation.longitude}
              locationName={selectedLocation.name}
              onBack={handleBackToMap}
            />
          ) : (
            <LocationSearch onLocationSelected={handleLocationSelected} />
          )
        } 
      />
  <Route path="/earthquake" element={<div><EarthquakePrediction /><PredictionHistory /></div>} />
  <Route path="/tsunami" element={<div><TsunamiPrediction /><PredictionHistory /></div>} />
    </Routes>
  );
}

function App() {
  return (
    <PredictionProvider>
      <div className="App">
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </div>
    </PredictionProvider>
  );
}

export default App;
