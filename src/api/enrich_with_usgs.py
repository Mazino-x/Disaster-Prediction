"""enrich_with_usgs.py

Join tsunami event CSV with nearest USGS earthquake events within a time window and radius.
Creates derived seismic features and a binary label based on Maximum Water Height.

Usage:
  python enrich_with_usgs.py --input <tsunami.csv> --output data/tsunami_enriched.csv

Defaults: time window +/-1 day, radius 200 km, label rule: Maximum Water Height (m) >= 0.5 => label=1
"""
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import time
import pandas as pd
import requests
from haversine import haversine, Unit

USGS_QUERY_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query.csv"


def parse_event_datetime(row):
    # Expect Year, Mo, Dy, Hr, Mn, Sec columns (as in your CSV)
    try:
        year = int(row.get('Year'))
        mo = int(row.get('Mo')) if 'Mo' in row else int(row.get('Month'))
        dy = int(row.get('Dy')) if 'Dy' in row else int(row.get('Day'))
        hr = int(row.get('Hr', 0))
        mn = int(row.get('Mn', 0))
        sec = int(row.get('Sec', 0))
        return datetime(year, mo, dy, hr, mn, sec)
    except Exception:
        return None


def query_usgs(lat, lon, starttime, endtime, maxradiuskm=200, minmagnitude=0):
    params = {
        'format': 'geojson',
        'starttime': starttime.isoformat(),
        'endtime': endtime.isoformat(),
        'latitude': lat,
        'longitude': lon,
        'maxradiuskm': maxradiuskm,
        'minmagnitude': minmagnitude
    }
    # Use CSV endpoint for simpler parsing
    params_csv = params.copy()
    params_csv['format'] = 'csv'
    resp = requests.get(USGS_QUERY_URL, params=params_csv, timeout=30)
    if resp.status_code != 200:
        return None
    try:
        df = pd.read_csv(pd.compat.StringIO(resp.text))
        return df
    except Exception:
        return None


def enrich_row(row, time_window_days=1, maxradiuskm=200):
    lat = row.get('Latitude')
    lon = row.get('Longitude')
    if pd.isna(lat) or pd.isna(lon):
        return {}
    dt = parse_event_datetime(row)
    if dt is None:
        # fallback: no datetime
        start = datetime(1800, 1, 1)
        end = datetime.now()
    else:
        start = dt - timedelta(days=time_window_days)
        end = dt + timedelta(days=time_window_days)

    usgs_df = query_usgs(lat, lon, start, end, maxradiuskm=maxradiuskm)
    if usgs_df is None or usgs_df.empty:
        return {}

    # find nearest earthquake by distance
    usgs_df['distance_km'] = usgs_df.apply(lambda r: haversine((lat, lon), (r['latitude'], r['longitude']), unit=Unit.KILOMETERS), axis=1)
    usgs_df = usgs_df.sort_values('distance_km')
    best = usgs_df.iloc[0]

    enriched = {
        'eq_mag': best.get('mag'),
        'eq_depth_km': best.get('depth'),
        'eq_nst': best.get('nst') if 'nst' in best.index else None,
        'eq_dmin': best.get('dmin') if 'dmin' in best.index else None,
        'eq_gap': best.get('gap') if 'gap' in best.index else None,
        'eq_magType': best.get('magType') if 'magType' in best.index else None,
        'eq_distance_km': best.get('distance_km')
    }
    return enriched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='data/tsunami_enriched.csv')
    parser.add_argument('--time-window-days', type=float, default=1.0)
    parser.add_argument('--maxradiuskm', type=float, default=200.0)
    parser.add_argument('--label-threshold', type=float, default=0.5, help='Maximum Water Height (m) threshold for label=1')
    parser.add_argument('--max-rows', type=int, default=0, help='If >0, limit processing to first N rows (for testing)')
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input file {inp} not found")

    df = pd.read_csv(inp)
    enriched_rows = []
    total = len(df)
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            e = enrich_row(row, time_window_days=args.time_window_days, maxradiuskm=args.maxradiuskm)
        except Exception as ex:
            print(f"Warning: enrich failed for row {i}: {ex}")
            e = {}
        enriched_rows.append(e)
        if i % 50 == 0:
            print(f"Processed {i}/{total} rows")
        if args.max_rows and i >= args.max_rows:
            print(f"Reached max-rows={args.max_rows}, stopping early")
            break
        time.sleep(0.1)  # be polite to USGS API

    enrich_df = pd.DataFrame(enriched_rows)
    out = pd.concat([df.reset_index(drop=True), enrich_df.reset_index(drop=True)], axis=1)

    # Create label based on Maximum Water Height (m)
    mwh_col = None
    for c in out.columns:
        if 'Maximum Water Height' in c or 'Maximum Water Height (m)' in c:
            mwh_col = c
            break
    if mwh_col is None and 'Maximum Water Height (m)' in out.columns:
        mwh_col = 'Maximum Water Height (m)'

    if mwh_col is not None:
        out['label'] = out[mwh_col].apply(lambda v: 1 if pd.notna(v) and float(v) >= args.label_threshold else 0)
    else:
        # If not present, default label 0
        out['label'] = 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote enriched CSV to {out_path}")


if __name__ == '__main__':
    main()
