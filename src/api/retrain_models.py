"""retrain_models.py

Small training harness to (re)train the models used by the API.

Usage (example):
  python retrain_models.py --task earthquake --data ../data/earthquake.csv --outdir models

Expectations for input CSV:
  - The CSV must contain all feature columns required by the model in any order.
  - The target column must be named "label" and contain 0/1 values.
  - Feature names should match exactly the names printed by `discover_features.py` (case-sensitive).

This script is a template and uses a simple sklearn pipeline (StandardScaler + RandomForest).
Customize the estimator and preprocessing as needed for better accuracy.
"""
import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report


MODEL_SPECS = {
    'earthquake': {
        'features': ['Latitude', 'Longitude', 'Depth', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second'],
        'out_name': 'earthquake_model.joblib'
    },
    'tsunami': {
        'features': ['magnitude', 'cdi', 'mmi', 'sig', 'nst', 'dmin', 'gap', 'depth', 'latitude', 'longitude', 'Year', 'Month', 'magType'],
        'out_name': 'tsunami_model.joblib'
    },
    # flood removed per project change
}


def _case_insensitive_map(columns):
    # helper: map lowercased column names to actual
    return {c.lower(): c for c in columns}


def map_columns(df_cols, required_features):
    """Try to map required_features (exact names) to df columns using
    case-insensitive matching and common aliases.
    Returns a dict feature -> column_name_in_df or raises ValueError.
    """
    col_map = _case_insensitive_map(df_cols)
    aliases = {
        'latitude': ['latitude', 'lat'],
        'longitude': ['longitude', 'lon', 'lng'],
        'magnitude': ['magnitude', 'mag'],
        'depth': ['depth'],
        'year': ['year'],
        'month': ['month'],
        'day': ['day'],
        'hour': ['hour'],
        'minute': ['minute', 'min'],
        'second': ['second', 'sec'],
        'magtype': ['magtype', 'mag_type'],
        'cdi': ['cdi'],
        'mmi': ['mmi'],
        'sig': ['sig'],
        'nst': ['nst'],
        'dmin': ['dmin'],
        'gap': ['gap'],
        'monsoonintensity': ['monsoonintensity', 'monsoon_intensity', 'monsoon']
    }

    mapping = {}
    for feat in required_features:
        key = feat.lower()
        # direct match
        if key in col_map:
            mapping[feat] = col_map[key]
            continue
        # aliases
        found = False
        if key in aliases:
            for a in aliases[key]:
                if a in col_map:
                    mapping[feat] = col_map[a]
                    found = True
                    break
        if found:
            continue
        # try fuzzy substring match
        for c_lower, actual in col_map.items():
            if key in c_lower or c_lower in key:
                mapping[feat] = actual
                found = True
                break
        if not found:
            raise ValueError(f"Cannot map required feature '{feat}' to any column in CSV. Available columns: {list(df_cols)}")
    return mapping


def train_task(task, data_path, outdir, test_size=0.2, random_state=42, label_col='label', dry_run=False):
    spec = MODEL_SPECS.get(task)
    if spec is None:
        raise ValueError(f"Unknown task: {task}. Valid: {list(MODEL_SPECS.keys())}")

    df = pd.read_csv(data_path)

    # Map required features to df columns flexibly
    try:
        mapping = map_columns(df.columns, spec['features'])
    except ValueError as e:
        raise

    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in CSV. Available columns: {list(df.columns)}")

    # Build X using mapped column names in the correct model feature order
    X = df[[mapping[f] for f in spec['features']]]
    X.columns = spec['features']  # rename to canonical order
    y = df[label_col].astype(int)

    if dry_run:
        print("Dry run mapping result:")
        for f in spec['features']:
            print(f"  {f} <- {mapping[f]}")
        print(f"Label column: {label_col}")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1))
    ])

    print(f"Training {task} on {len(X_train)} rows, validating on {len(X_test)} rows...")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Validation accuracy: {acc:.4f}")
    print(classification_report(y_test, preds))

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / spec['out_name']
    joblib.dump(pipeline, out_path)
    print(f"Saved model to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True, choices=list(MODEL_SPECS.keys()))
    parser.add_argument('--data', required=True, help='Path to CSV with training data')
    parser.add_argument('--outdir', default=str(Path(__file__).parent / 'models'), help='Where to write model artifacts')
    parser.add_argument('--label-col', default='label', help='Name of the label column in the CSV')
    parser.add_argument('--dry-run', action='store_true', help='Validate column mapping and exit without training')
    args = parser.parse_args()

    train_task(args.task, args.data, args.outdir, label_col=args.label_col, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
