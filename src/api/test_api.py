import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('main', str(Path(__file__).parent / 'main.py'))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app

with app.test_client() as client:
    # Earthquake model: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second (IN THIS ORDER)
    resp = client.post('/earthquake', json={
        'Latitude': 12.34, 'Longitude': 56.78, 'Depth': 10, 
        'Year': 2023, 'Month': 1, 'Day': 15,
        'Hour': 12, 'Minute': 30, 'Second': 45
    })
    print('EARTHQUAKE', resp.status_code, resp.get_data(as_text=True))

    # Tsunami model: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Sec
    resp = client.post('/tsunami', json={
        'Latitude': 12.34, 'Longitude': 56.78, 'Tsunami Magnitude (Iida)': 6.5,
        'Year': 2023, 'Mo': 1, 'Dy': 15,
        'Hr': 12, 'Mn': 30, 'Sec': 45
    })
    print('TSUNAMI', resp.status_code, resp.get_data(as_text=True))
