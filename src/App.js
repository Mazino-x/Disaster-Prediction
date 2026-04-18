import './App.css';
import Front from './Front';
import EarthquakePrediction from './EarthquakePrediction';
import TsunamiPrediction from './TsunamiPrediction';
import LocationSearch from './LocationSearch';
import LocationPredictionDashboard from './LocationPredictionDashboard';
import PredictionHistory from './PredictionHistory';
import { PredictionProvider } from './PredictionContext';
import { BrowserRouter, Route, Routes, useNavigate, useLocation, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Navbar() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const [currentTime, setCurrentTime] = useState(new Date());
  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState('');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!navigator.geolocation) {
      setWeatherError('Geolocation unavailable');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const response = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true&timezone=auto`
          );
          const data = await response.json();
          if (!data.current_weather) {
            throw new Error('Weather unavailable');
          }
          const code = data.current_weather.weathercode;
          const description = getWeatherDescription(code);
          setWeather({
            temperature: Math.round(data.current_weather.temperature),
            description,
          });
        } catch (err) {
          setWeatherError('Weather unavailable');
        }
      },
      () => {
        setWeatherError('Location permission denied');
      },
      { timeout: 10000 }
    );
  }, []);

  const formatTime = (date) => {
    return date.toLocaleString(undefined, {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getWeatherDescription = (code) => {
    const map = {
      0: 'Clear',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Fog',
      48: 'Fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      61: 'Rain',
      63: 'Rain',
      65: 'Heavy rain',
      71: 'Snow',
      73: 'Snow',
      75: 'Snow',
      80: 'Rain showers',
      81: 'Rain showers',
      82: 'Heavy showers',
      95: 'Thunderstorm',
      96: 'Thunderstorm',
      99: 'Thunderstorm',
    };
    return map[code] || 'Weather';
  };

  return (
    <nav className="appNavbar">
      <Link to="/" className="navLogo">
        <span className="navLogoIcon">🌍</span>
        <span>DisasterPredict</span>
      </Link>
      <div className="navbarRight">
        {!isHome && (
          <div className="navLinks">
            <Link to="/location" className={`navLink ${location.pathname === '/location' || location.pathname === '/predictions' ? 'active' : ''}`}>Risk Map</Link>
            <Link to="/earthquake" className={`navLink ${location.pathname === '/earthquake' ? 'active' : ''}`}>Earthquake</Link>
            <Link to="/tsunami" className={`navLink ${location.pathname === '/tsunami' ? 'active' : ''}`}>Tsunami</Link>
          </div>
        )}
        <div className="topRightInfo">
          <div className="currentTime">{formatTime(currentTime)}</div>
          <div className="weatherInfo">
            {weather
              ? `${weather.description}, ${weather.temperature}°C`
              : weatherError || 'Loading weather...'}
          </div>
        </div>
      </div>
    </nav>
  );
}

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
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Front />} />
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
        <Route path="/earthquake" element={<><EarthquakePrediction /><PredictionHistory /></>} />
        <Route path="/tsunami" element={<><TsunamiPrediction /><PredictionHistory /></>} />
      </Routes>
    </>
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
