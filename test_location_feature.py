#!/usr/bin/env python3
"""
Test script to verify location-based disaster predictions work correctly.
This simulates what the LocationPredictionDashboard component will do.
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'

def test_location_predictions(latitude, longitude, location_name):
    """Test all 3 prediction endpoints for a specific location"""
    
    print(f"\n{'='*60}")
    print(f"Testing Disaster Predictions for: {location_name}")
    print(f"Coordinates: ({latitude:.4f}, {longitude:.4f})")
    print(f"{'='*60}\n")
    
    now = datetime.now()
    
    # Test Earthquake Prediction
    print("🌍 EARTHQUAKE PREDICTION")
    print("-" * 40)
    earthquake_payload = {
        "Latitude": latitude,
        "Longitude": longitude,
        "Depth": 10,
        "Year": now.year,
        "Month": now.month,
        "Day": now.day,
        "Hour": now.hour,
        "Minute": now.minute,
        "Second": now.second
    }
    
    try:
        response = requests.post(f'{BASE_URL}/earthquake', json=earthquake_payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction')
            risk = "HIGH RISK ⚠️" if prediction == 1 else "LOW RISK ✓"
            print(f"Status: {response.status_code} OK")
            print(f"Risk Level: {risk}")
            print(f"Prediction: {prediction}")
        else:
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Flood prediction removed from this test (project configured for earthquake and tsunami)
    
    # Test Tsunami Prediction
    print("\n🌊 TSUNAMI PREDICTION")
    print("-" * 40)
    tsunami_payload = {
        "magnitude": 5.0,
        "cdi": 1,
        "mmi": 1,
        "sig": 100,
        "nst": 10,
        "dmin": 0,
        "gap": 0,
        "depth": 10,
        "latitude": latitude,
        "longitude": longitude,
        "Year": now.year,
        "Month": now.month,
        "magType": 0
    }
    
    try:
        response = requests.post(f'{BASE_URL}/tsunami', json=tsunami_payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction')
            risk = "HIGH RISK ⚠️" if prediction == 1 else "LOW RISK ✓"
            print(f"Status: {response.status_code} OK")
            print(f"Risk Level: {risk}")
            print(f"Prediction: {prediction}")
        else:
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    # Test with some known locations
    test_location_predictions(40.7128, -74.0060, "New York City, USA")
    test_location_predictions(35.6762, 139.6503, "Tokyo, Japan")
    test_location_predictions(-33.8688, 151.2093, "Sydney, Australia")
    test_location_predictions(37.7749, -122.4194, "San Francisco, USA")
