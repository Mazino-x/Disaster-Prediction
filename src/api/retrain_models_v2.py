"""
Enhanced model retraining script with better data preparation and class balancing.
Uses NOAA/USGS data with improved labeling and balanced training.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime, timedelta
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import warnings
warnings.filterwarnings('ignore')


class TsunamiTrainer:
    """Train tsunami classifier from NOAA historical data."""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self):
        """Load NOAA tsunami CSV."""
        print(f"\n{'='*60}")
        print("TSUNAMI MODEL TRAINING - NOAA DATA")
        print(f"{'='*60}")
        print(f"Loading data from {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} tsunami records")
        
    def prepare_features(self):
        """Extract and prepare features."""
        print("\nPreparing features...")
        
        # Define feature columns expected by model
        feature_cols = ['Latitude', 'Longitude', 'Tsunami Magnitude (Iida)', 'Year', 'Mo', 'Dy', 'Hr', 'Mn', 'Sec']
        
        # Fill missing values strategically
        self.df['Latitude'] = pd.to_numeric(self.df['Latitude'], errors='coerce').fillna(0)
        self.df['Longitude'] = pd.to_numeric(self.df['Longitude'], errors='coerce').fillna(0)
        self.df['Tsunami Magnitude (Iida)'] = pd.to_numeric(self.df['Tsunami Magnitude (Iida)'], errors='coerce').fillna(0)
        self.df['Year'] = pd.to_numeric(self.df['Year'], errors='coerce').fillna(0).astype(int)
        self.df['Mo'] = pd.to_numeric(self.df['Mo'], errors='coerce').fillna(6).astype(int)  # Default to June
        self.df['Dy'] = pd.to_numeric(self.df['Dy'], errors='coerce').fillna(15).astype(int)  # Default to 15th
        self.df['Hr'] = pd.to_numeric(self.df['Hr'], errors='coerce').fillna(12).astype(int)  # Default to noon
        self.df['Mn'] = pd.to_numeric(self.df['Mn'], errors='coerce').fillna(0).astype(int)
        self.df['Sec'] = pd.to_numeric(self.df['Sec'], errors='coerce').fillna(0).astype(int)
        
        # Clamp values to valid ranges
        self.df['Mo'] = self.df['Mo'].clip(1, 12)
        self.df['Dy'] = self.df['Dy'].clip(1, 31)
        self.df['Hr'] = self.df['Hr'].clip(0, 23)
        self.df['Mn'] = self.df['Mn'].clip(0, 59)
        self.df['Sec'] = self.df['Sec'].clip(0, 59)
        
        # Extract features
        X = self.df[feature_cols].copy()
        
        # Better labeling: use "Tsunami Event Validity" + Maximum Water Height
        # Validity codes: 4=definite tsunami, 3=probably, 2=possible, 1=uncertain, 0=non-tsunami
        mwh_col = 'Maximum Water Height (m)'
        validity_col = 'Tsunami Event Validity'
        
        # Create label: 1 if definite tsunami (validity >= 3) OR water height >= 0.5m
        y = ((self.df[validity_col].astype(float) >= 3) | 
             (pd.to_numeric(self.df[mwh_col], errors='coerce') >= 0.5)).astype(int)
        
        print(f"Features: {feature_cols}")
        print(f"Label distribution: {y.value_counts().to_dict()}")
        print(f"  Class 0 (No/Uncertain Tsunami): {(y == 0).sum()}")
        print(f"  Class 1 (Definite Tsunami): {(y == 1).sum()}")
        
        return X, y
    
    def train(self, X, y):
        """Train model with class weighting."""
        print("\nSplitting data (80/20 train/test)...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(self.X_train)} samples")
        print(f"Test set: {len(self.X_test)} samples")
        
        # Compute class weights to handle imbalance
        class_weights = compute_class_weight(
            'balanced', 
            classes=np.unique(self.y_train), 
            y=self.y_train
        )
        class_weight_dict = {i: w for i, w in enumerate(class_weights)}
        print(f"Class weights: {class_weight_dict}")
        
        print("\nTraining RandomForest (200 trees, balanced classes)...")
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                n_jobs=-1,
                random_state=42,
                class_weight=class_weight_dict,
                min_samples_split=5,
                min_samples_leaf=2,
                max_depth=15
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_preds = pipeline.predict(self.X_train)
        test_preds = pipeline.predict(self.X_test)
        
        train_acc = accuracy_score(self.y_train, train_preds)
        test_acc = accuracy_score(self.y_test, test_preds)
        
        print(f"\nTraining accuracy: {train_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        print("\nClassification Report (Test Set):")
        print(classification_report(self.y_test, test_preds, target_names=['No Tsunami', 'Tsunami']))
        
        print("Confusion Matrix (Test Set):")
        cm = confusion_matrix(self.y_test, test_preds)
        print(cm)
        
        return pipeline
    
    def save_model(self, pipeline, output_dir: Path):
        """Save trained model."""
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / 'tsunami_model.joblib'
        joblib.dump(pipeline, out_path)
        print(f"\n✓ Tsunami model saved to {out_path}")
        return out_path


class EarthquakeTrainer:
    """Train earthquake classifier from USGS data."""
    
    def __init__(self):
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def fetch_usgs_data(self, min_magnitude=3.0, days_back=3650, max_events=10000):
        """Fetch earthquake data from USGS API."""
        print(f"\n{'='*60}")
        print("EARTHQUAKE MODEL TRAINING - USGS DATA")
        print(f"{'='*60}")
        print(f"Fetching earthquakes from USGS...")
        print(f"  Minimum magnitude: {min_magnitude}")
        print(f"  Days back: {days_back}")
        print(f"  Max events: {max_events}")
        
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
                print(f"Error: USGS returned status {resp.status_code}")
                return None
            
            from io import StringIO
            df = pd.read_csv(StringIO(resp.text))
            print(f"✓ Fetched {len(df)} earthquake records")
            return df
        except Exception as e:
            print(f"Error fetching USGS data: {e}")
            return None
    
    def load_data(self, csv_path: str = None):
        """Load earthquake data from CSV or fetch from USGS."""
        if csv_path:
            print(f"Loading earthquake data from {csv_path}")
            self.df = pd.read_csv(csv_path)
        else:
            # Fetch from USGS (10 years of data with varied magnitudes)
            self.df = self.fetch_usgs_data(min_magnitude=3.0, days_back=3650, max_events=10000)
            if self.df is None:
                raise SystemExit("Failed to fetch earthquake data from USGS")
        
        print(f"Loaded {len(self.df)} earthquake records")
        
    def prepare_features(self):
        """Extract and prepare earthquake features."""
        print("\nPreparing features...")
        
        # Standardize column names
        self.df = self.df.rename(columns={
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'depth': 'Depth',
            'mag': 'Magnitude'
        })
        
        # Extract datetime components
        self.df['time'] = pd.to_datetime(self.df['time'], errors='coerce')
        self.df['Year'] = self.df['time'].dt.year
        self.df['Month'] = self.df['time'].dt.month
        self.df['Day'] = self.df['time'].dt.day
        self.df['Hour'] = self.df['time'].dt.hour
        self.df['Minute'] = self.df['time'].dt.minute
        self.df['Second'] = self.df['time'].dt.second
        
        # Define feature columns
        feature_cols = ['Latitude', 'Longitude', 'Depth', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
        
        # Extract and clean features
        X = self.df[feature_cols].copy()
        X = X.fillna(0)
        
        # Create binary label: 
        # Class 1 = Significant earthquake (magnitude >= 5.5) - these cause damage
        # Class 0 = Moderate earthquake (3.0-5.5) - mostly felt but limited damage
        y = (self.df['Magnitude'] >= 5.5).astype(int)
        
        print(f"Features: {feature_cols}")
        print(f"Magnitude range: {self.df['Magnitude'].min():.1f} - {self.df['Magnitude'].max():.1f}")
        print(f"Label distribution: {y.value_counts().to_dict()}")
        print(f"  Class 0 (Moderate, M < 5.5): {(y == 0).sum()}")
        print(f"  Class 1 (Significant, M >= 5.5): {(y == 1).sum()}")
        
        # Print geographic coverage
        print(f"\nGeographic coverage:")
        print(f"  Latitude range: {self.df['Latitude'].min():.1f} - {self.df['Latitude'].max():.1f}")
        print(f"  Longitude range: {self.df['Longitude'].min():.1f} - {self.df['Longitude'].max():.1f}")
        print(f"  Depth range: {self.df['Depth'].min():.1f} - {self.df['Depth'].max():.1f} km")
        
        return X, y
    
    def train(self, X, y):
        """Train model with class weighting."""
        print("\nSplitting data (80/20 train/test)...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(self.X_train)} samples")
        print(f"Test set: {len(self.X_test)} samples")
        
        # Compute class weights
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(self.y_train),
            y=self.y_train
        )
        class_weight_dict = {i: w for i, w in enumerate(class_weights)}
        print(f"Class weights: {class_weight_dict}")
        
        print("\nTraining RandomForest (200 trees, balanced classes)...")
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                n_jobs=-1,
                random_state=42,
                class_weight=class_weight_dict,
                min_samples_split=5,
                min_samples_leaf=2,
                max_depth=15
            ))
        ])
        
        pipeline.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_preds = pipeline.predict(self.X_train)
        test_preds = pipeline.predict(self.X_test)
        
        train_acc = accuracy_score(self.y_train, train_preds)
        test_acc = accuracy_score(self.y_test, test_preds)
        
        print(f"\nTraining accuracy: {train_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        print("\nClassification Report (Test Set):")
        print(classification_report(self.y_test, test_preds, target_names=['Moderate', 'Significant']))
        
        print("Confusion Matrix (Test Set):")
        cm = confusion_matrix(self.y_test, test_preds)
        print(cm)
        
        # Feature importances
        clf = pipeline.named_steps['clf']
        importances = clf.feature_importances_
        feature_names = ['Latitude', 'Longitude', 'Depth', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
        print("\nTop 5 Feature Importances:")
        top_indices = np.argsort(importances)[-5:][::-1]
        for idx in top_indices:
            print(f"  {feature_names[idx]:12s}: {importances[idx]:.4f}")
        
        return pipeline
    
    def save_model(self, pipeline, output_dir: Path):
        """Save trained model."""
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / 'earthquake_model.joblib'
        joblib.dump(pipeline, out_path)
        print(f"\n✓ Earthquake model saved to {out_path}")
        return out_path


def main():
    parser = argparse.ArgumentParser(description='Retrain disaster prediction models with balanced data')
    parser.add_argument('--tsunami-csv', help='Path to NOAA tsunami CSV')
    parser.add_argument('--earthquake-csv', help='Path to earthquake CSV (or fetch from USGS)')
    parser.add_argument('--outdir', default=str(Path(__file__).parent / 'models'), help='Output directory')
    parser.add_argument('--earthquake-only', action='store_true', help='Only retrain earthquake model')
    parser.add_argument('--tsunami-only', action='store_true', help='Only retrain tsunami model')
    args = parser.parse_args()
    
    output_dir = Path(args.outdir)
    
    # Train Tsunami Model
    if not args.earthquake_only:
        if not args.tsunami_csv:
            print("ERROR: Tsunami CSV path required (--tsunami-csv)")
            return
        
        try:
            tsunami_trainer = TsunamiTrainer(args.tsunami_csv)
            tsunami_trainer.load_data()
            X, y = tsunami_trainer.prepare_features()
            pipeline = tsunami_trainer.train(X, y)
            tsunami_trainer.save_model(pipeline, output_dir)
        except Exception as e:
            print(f"\n✗ Error training tsunami model: {e}")
            import traceback
            traceback.print_exc()
    
    # Train Earthquake Model
    if not args.tsunami_only:
        try:
            earthquake_trainer = EarthquakeTrainer()
            earthquake_trainer.load_data(args.earthquake_csv)
            X, y = earthquake_trainer.prepare_features()
            pipeline = earthquake_trainer.train(X, y)
            earthquake_trainer.save_model(pipeline, output_dir)
        except Exception as e:
            print(f"\n✗ Error training earthquake model: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("RETRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Models saved to: {output_dir}")


if __name__ == '__main__':
    main()
