"""Fetch earthquake data from USGS and train earthquake classifier."""
import argparse
from pathlib import Path
import pandas as pd
import joblib
import requests
from datetime import datetime, timedelta
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def fetch_usgs_earthquakes(min_magnitude=4.0, days_back=365, max_events=5000):
    """Fetch earthquake data from USGS API."""
    print(f'Fetching earthquakes from USGS (magnitude >= {min_magnitude}, last {days_back} days)...')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)
    
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query.csv'
    params = {
        'starttime': start_time.isoformat(),
        'endtime': end_time.isoformat(),
        'minmagnitude': min_magnitude,
        'orderby': 'magnitude',
        'limit': max_events
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            print(f'Error: USGS returned status {resp.status_code}')
            return None
        
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
        print(f'Fetched {len(df)} earthquake records')
        return df
    except Exception as e:
        print(f'Error fetching USGS data: {e}')
        return None


def prepare_earthquake_data(df):
    """Prepare earthquake data for training."""
    df = df.rename(columns={
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'depth': 'Depth',
        'mag': 'Magnitude'
    })
    
    df['Year'] = pd.to_datetime(df['time']).dt.year
    df['Month'] = pd.to_datetime(df['time']).dt.month
    df['Day'] = pd.to_datetime(df['time']).dt.day
    df['Hour'] = pd.to_datetime(df['time']).dt.hour
    df['Minute'] = pd.to_datetime(df['time']).dt.minute
    df['Second'] = pd.to_datetime(df['time']).dt.second
    
    feature_cols = ['Latitude', 'Longitude', 'Depth', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
    df_clean = df[feature_cols].copy()
    df_clean = df_clean.fillna(0)
    
    # Create binary label: magnitude >= 5.0 is significant
    y = (df['Magnitude'] >= 5.0).astype(int)
    
    return df_clean, y, feature_cols


def main():
    parser = argparse.ArgumentParser(description='Fetch and train earthquake classifier')
    parser.add_argument('--data', help='Path to earthquake CSV (if provided, skip fetch)')
    parser.add_argument('--outdir', default=str(Path(__file__).parent / 'models'), help='Output directory')
    parser.add_argument('--min-magnitude', type=float, default=4.0, help='Minimum magnitude to fetch')
    parser.add_argument('--days-back', type=int, default=365, help='Days of history to fetch')
    args = parser.parse_args()
    
    if args.data:
        print(f'Loading earthquake data from {args.data}')
        df = pd.read_csv(args.data)
    else:
        df = fetch_usgs_earthquakes(min_magnitude=args.min_magnitude, days_back=args.days_back)
        if df is None:
            raise SystemExit('Failed to fetch earthquake data')
    
    print(f'Preparing {len(df)} records...')
    X, y, feature_cols = prepare_earthquake_data(df)
    
    print(f'Label distribution: {y.value_counts().to_dict()}')
    print(f'Features: {feature_cols}')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42))
    ])
    
    print(f'Training on {len(X_train)} rows; validating on {len(X_test)} rows')
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    print(f'Validation accuracy: {accuracy_score(y_test, preds):.4f}')
    print(classification_report(y_test, preds))
    
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / 'earthquake_model.joblib'
    joblib.dump(pipeline, out_path)
    print(f'Saved model to {out_path}')


if __name__ == '__main__':
    main()
