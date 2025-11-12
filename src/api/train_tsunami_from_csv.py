"""Train a tsunami classifier directly from the provided tsunami CSV."""
import argparse
from pathlib import Path
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def find_column(cols, candidates):
    """Find a column by candidate names (case-insensitive)."""
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    for c_lower, actual in cols_lower.items():
        for cand in candidates:
            if cand.lower() in c_lower or c_lower in cand.lower():
                return actual
    return None


def build_features(df):
    """Extract feature columns from the tsunami CSV."""
    cols = df.columns.tolist()
    lat_col = find_column(cols, ['Latitude', 'lat'])
    lon_col = find_column(cols, ['Longitude', 'lon', 'lng'])
    mag_col = find_column(cols, ['Tsunami Magnitude (Iida)', 'Tsunami Magnitude', 'Earthquake Magnitude', 'mag', 'magnitude'])
    year_col = find_column(cols, ['Year', 'year'])
    month_col = find_column(cols, ['Mo', 'Month', 'month', 'mo'])
    day_col = find_column(cols, ['Dy', 'Day', 'day', 'dy'])
    hour_col = find_column(cols, ['Hr', 'Hour', 'hour'])
    minute_col = find_column(cols, ['Mn', 'Minute', 'minute', 'min'])
    second_col = find_column(cols, ['Sec', 'Second', 'second', 'sec'])

    feature_cols = []
    if lat_col and lon_col:
        feature_cols += [lat_col, lon_col]
    if mag_col:
        feature_cols.append(mag_col)
    for c in [year_col, month_col, day_col, hour_col, minute_col, second_col]:
        if c and c not in feature_cols:
            feature_cols.append(c)

    return feature_cols


def main():
    parser = argparse.ArgumentParser(description='Train tsunami classifier from CSV')
    parser.add_argument('--data', required=True, help='Path to tsunami CSV file')
    parser.add_argument('--outdir', default=str(Path(__file__).parent / 'models'), help='Output directory for model')
    parser.add_argument('--label-threshold', type=float, default=0.5, help='Label threshold (Maximum Water Height in meters)')
    args = parser.parse_args()

    print(f'Loading data from {args.data}')
    df = pd.read_csv(args.data)
    print(f'Loaded {len(df)} rows')

    feature_cols = build_features(df)
    if not feature_cols:
        raise SystemExit('No suitable feature columns found in CSV.')

    print(f'Using features: {feature_cols}')

    mwh_col = None
    for c in df.columns:
        if 'maximum water height' in c.lower():
            mwh_col = c
            break

    if mwh_col is None:
        raise SystemExit('No Maximum Water Height column found in CSV.')

    X = df[feature_cols].copy()
    X = X.fillna(0)
    y = df[mwh_col].apply(lambda v: 1 if pd.notna(v) and float(v) >= args.label_threshold else 0)

    print(f'Label distribution: {y.value_counts().to_dict()}')

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
    out_path = outdir / 'tsunami_model.joblib'
    joblib.dump(pipeline, out_path)
    print(f'Saved model to {out_path}')


if __name__ == '__main__':
    main()
