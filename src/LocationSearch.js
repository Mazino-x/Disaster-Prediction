import React, { useState, useCallback, memo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import './LocationSearch.css';
import REGIONS from './regions';

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const LocationMarker = memo(function LocationMarker({ onLocationSelect }) {
    const [position, setPosition] = useState(null);

    useMapEvents({
        click(e) {
            setPosition(e.latlng);
            onLocationSelect(e.latlng.lat, e.latlng.lng);
        },
    });

    if (position === null) return null;

    return (
        <Marker position={position}>
            <Popup>
                Latitude: {position.lat.toFixed(4)}<br />
                Longitude: {position.lng.toFixed(4)}
            </Popup>
        </Marker>
    );
});

// Separate map component so it doesn't rerender when LocationSearch state changes
const MapView = function MapView({ onLocationSelect }) {
    return (
        <MapContainer center={[20, 0]} zoom={2} preferCanvas={true} className="leafletMap">
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
            />
            <LocationMarker onLocationSelect={onLocationSelect} />
        </MapContainer>
    );
};

const MemoizedMap = memo(MapView);

function LocationSearch({ onLocationSelected }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [locationName, setLocationName] = useState('');
    const [searchError, setSearchError] = useState(null);

    const filteredRegions = searchTerm
        ? REGIONS.filter(region => region.label.toLowerCase().includes(searchTerm.toLowerCase()))
        : REGIONS;

    const handleRegionSelect = (region) => {
        setSearchTerm(region.label);
        setLatitude(region.latitude.toFixed(4));
        setLongitude(region.longitude.toFixed(4));
        setLocationName(region.label);
        setSearchError(null);
    };

    // Stable callback so memoized map children don't re-render unnecessarily
    const handleMapSelect = useCallback((lat, lng) => {
        setSearchTerm('');
        setLatitude(lat.toFixed(4));
        setLongitude(lng.toFixed(4));
        setLocationName(`(${lat.toFixed(4)}, ${lng.toFixed(4)})`);
        setSearchError(null);
    }, []);

    const handleSearchByCoordinates = () => {
        if (!latitude || !longitude) {
            setSearchError('Please enter both latitude and longitude');
            return;
        }
        const lat = parseFloat(latitude);
        const lng = parseFloat(longitude);
        if (isNaN(lat) || isNaN(lng)) {
            setSearchError('Invalid latitude or longitude');
            return;
        }
        if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
            setSearchError('Latitude must be -90 to 90, Longitude must be -180 to 180');
            return;
        }
        setLocationName(`(${lat.toFixed(4)}, ${lng.toFixed(4)})`);
        setSearchError(null);
        onLocationSelected(lat, lng, `Location: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    };

    const handleRegionSearchChange = (value) => {
        setSearchTerm(value);
        setLocationName('');
        setSearchError(null);
    };

    return (
        <div className="locationSearchContainer">
            <div className="locationHeader">
                <h2>Disaster Risk Assessment</h2>
                <p>Click on the map or enter coordinates to select a location</p>
            </div>

            <div className="locationInputSection">
                <div className="coordinateInputs">
                    <div className="inputGroup">
                        <label htmlFor="region-search">Search region or city</label>
                        <input
                            type="text"
                            id="region-search"
                            value={searchTerm}
                            onChange={(e) => handleRegionSearchChange(e.target.value)}
                            placeholder="e.g. Australia, Canada, Tokyo"
                            autoComplete="off"
                        />
                        {searchTerm && (
                          <div className="regionSuggestions">
                              {filteredRegions.slice(0, 8).map((region) => (
                                <button
                                  key={region.value}
                                  type="button"
                                  className="regionSuggestion"
                                  onClick={() => handleRegionSelect(region)}
                                >
                                  {region.label}
                                </button>
                              ))}
                          </div>
                        )}
                    </div>
                    <div className="inputGroup">
                        <label htmlFor="latitude">Latitude (-90 to 90):</label>
                        <input
                            type="number"
                            id="latitude"
                            value={latitude}
                            onChange={(e) => setLatitude(e.target.value)}
                            placeholder="e.g., 40.7128"
                            step="0.0001"
                            min="-90"
                            max="90"
                        />
                    </div>
                    <div className="inputGroup">
                        <label htmlFor="longitude">Longitude (-180 to 180):</label>
                        <input
                            type="number"
                            id="longitude"
                            value={longitude}
                            onChange={(e) => setLongitude(e.target.value)}
                            placeholder="e.g., -74.0060"
                            step="0.0001"
                            min="-180"
                            max="180"
                        />
                    </div>
                    <button onClick={handleSearchByCoordinates} className="searchBtn">
                        Search
                    </button>
                </div>
                {searchError && <div className="errorMessage">{searchError}</div>}
                {locationName && <div className="selectedLocation">Selected: {locationName}</div>}
            </div>

                    <div className="mapContainer">
                        {/* preferCanvas reduces DOM overhead for many vector layers/markers */}
                        <MemoizedMap onLocationSelect={handleMapSelect} />
                    </div>

            {latitude && longitude && (
                <button
                    onClick={() => onLocationSelected(parseFloat(latitude), parseFloat(longitude), locationName)}
                    className="predictBtn"
                >
                    Get Disaster Predictions for {locationName}
                </button>
            )}
        </div>
    );
}

export default LocationSearch;
