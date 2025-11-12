import importlib.util
import pandas as pd
from pathlib import Path

spec = importlib.util.spec_from_file_location('main', str(Path(__file__).parent / 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

earthquake_model = main.earthquake_model
tsunami_model = main.tsunami_model

# Get feature names from the models
print("=== EARTHQUAKE MODEL ===")
if hasattr(earthquake_model, 'feature_names_in_'):
    print(f"Feature names: {earthquake_model.feature_names_in_}")
else:
    print("No feature_names_in_ attribute")

print("\n=== TSUNAMI MODEL ===")
if hasattr(tsunami_model, 'feature_names_in_'):
    print(f"Feature names: {tsunami_model.feature_names_in_}")
else:
    print("No feature_names_in_ attribute")

# Try predicting with correct features in correct order
print("\n=== TESTING EARTHQUAKE ===")
try:
    # Correct order from model: ['Latitude' 'Longitude' 'Depth' 'Year' 'Month' 'Day' 'Hour' 'Minute' 'Second']
    eq_data = {
        'Latitude': [12.34],
        'Longitude': [56.78],
        'Depth': [10.0],
        'Year': [2023],
        'Month': [1],
        'Day': [15],
        'Hour': [12],
        'Minute': [30],
        'Second': [45]
    }
    df = pd.DataFrame(eq_data)
    # Reorder to match model's expected order
    df = df[['Latitude', 'Longitude', 'Depth', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']]
    pred = earthquake_model.predict(df)
    print("SUCCESS! Prediction = " + str(pred[0]))
except Exception as e:
    print("FAILED: " + str(e)[:300])

print("\n=== TESTING TSUNAMI ===")
try:
    # Correct order from model: ['magnitude' 'cdi' 'mmi' 'sig' 'nst' 'dmin' 'gap' 'depth' 'latitude' 'longitude' 'Year' 'Month' 'magType']
    # magType needs to be numeric (likely a category code)
    ts_data = {
        'magnitude': [6.5],
        'cdi': [5.0],
        'mmi': [7.0],
        'sig': [850],
        'nst': [100],
        'dmin': [10.0],
        'gap': [30.0],
        'depth': [10.0],
        'latitude': [12.34],
        'longitude': [56.78],
        'Year': [2023],
        'Month': [1],
        'magType': [1]  # Try numeric code instead of string
    }
    df = pd.DataFrame(ts_data)
    df = df[['magnitude', 'cdi', 'mmi', 'sig', 'nst', 'dmin', 'gap', 'depth', 'latitude', 'longitude', 'Year', 'Month', 'magType']]
    pred = tsunami_model.predict(df)
    print("SUCCESS! Prediction = " + str(pred[0]))
except Exception as e:
    print("FAILED: " + str(e)[:300])
