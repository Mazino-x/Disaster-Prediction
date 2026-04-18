# Copilot Instructions - Disaster Prediction# Copilot Instructions - Disaster Prediction# Copilot Instructions - Disaster Prediction# Copilot Instructions � Disaster Prediction



A React frontend + Flask ML backend for earthquake and tsunami risk predictions by location.



## Project GoalA React frontend + Flask ML backend for earthquake and tsunami risk predictions.



Give users a website where they can:

1. Input a location or select it on a map

2. Receive predictions about whether that area is prone to earthquakes or tsunamis## TL;DR - Essential ContextA React frontend + Flask ML backend for earthquake and tsunami risk predictions.A React frontend + Flask ML backend for earthquake and tsunami risk predictions.



## Current Implementation



**✅ Workflow**: Home → Feature Selection → Location Input/Map → Predictions DashboardThis is a form → API → scikit-learn model → result display pipeline. The critical gotcha: model feature names and order are rigid. Always run `python src/api/discover_features.py` before modifying forms or payloads. Use PredictionContext for cross-route state.



**✅ Location Selection Methods**:

- Click on interactive map (react-leaflet)

- Enter latitude/longitude coordinates manually## Architecture## TL;DR - Essential Context## TL;DR � Essential Context

- Both with validation (lat: -90 to 90, lng: -180 to 180)



**✅ Predictions Delivered**:

- Earthquake risk: Low (0) or High (1)**Frontend** (React 18 + React Router in src/)

- Tsunami risk: Low (0) or High (1)

- Color-coded indicators (green=low, red=high)- Routes: Home → Location/Earthquake/Tsunami prediction forms → PredictionHistory

- Risk labels with explanatory text

- Current date/time used for time-based features- Global state: PredictionContext.js (React Context, session-persisted)This is a form → API → scikit-learn model → result display pipeline. The critical gotcha: **model feature names and order are rigid**. Always run `python src/api/discover_features.py` before modifying forms or payloads. Use `PredictionContext` for cross-route state.This is a **form  API  scikit-learn model  result display** pipeline. The critical gotcha: **model feature names and order are rigid**. Always run python src/api/discover_features.py before modifying forms or payloads. Use PredictionContext for cross-route state.



## Architecture- Prediction components: EarthquakePrediction.js, TsunamiPrediction.js



**Frontend** (React 18, `src/`)- Map components: LocationSearch.js, LocationPredictionDashboard.js (react-leaflet)

- `Front.js`: Landing page with feature cards

- `Features.js`: Buttons to Location/Earthquake/Tsunami routes

- `LocationSearch.js`: Map + coordinate input component

- `LocationPredictionDashboard.js`: Results display (auto-fetches both predictions)**Backend** (Flask in src/api/main.py)## Architecture## Architecture

- `PredictionContext.js`: Global state for prediction history

- `App.js`: Router with PredictionProvider wrapper- Three endpoints: POST /earthquake, /tsunami, /forestfire



**Backend** (Flask, `src/api/main.py`)- Each loads a pre-trained scikit-learn model from src/api/models/

- `/earthquake`: POST with Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second

- `/tsunami`: POST with Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Sec- Core logic: _predict(model, data) helper handles DataFrame construction, column reordering, and numpy to JSON conversion

- Models: scikit-learn RandomForest classifiers in `src/api/models/`

- Production: wsgi.py exposes Flask app for Gunicorn**Frontend** (React 18 + React Router in `src/`)**Frontend** (React 18 + React Router in src/)

## Quick Start



```powershell

# Backend## Setup & Quick Start- Routes: Home → Location/Earthquake/Tsunami prediction forms → PredictionHistory (shared on each page)- Routes: Home  Location/Earthquake/Tsunami prediction forms  PredictionHistory (shared on each page)

python src/api/main.py



# Frontend (separate terminal)

npm install```powershell- Global state: `PredictionContext.js` (React Context, session-persisted)- Global state: PredictionContext.js (React Context, session-persisted)

npm start

# Install dependencies

# Visit http://localhost:3000

```pip install -r requirements.txt- Prediction components: `EarthquakePrediction.js`, `TsunamiPrediction.js`- Prediction components: EarthquakePrediction.js, TsunamiPrediction.js



## Critical Patternsnpm install



### Feature Name Mapping- Map components: `LocationSearch.js`, `LocationPredictionDashboard.js` (react-leaflet)- Map components: LocationSearch.js, LocationPredictionDashboard.js (react-leaflet)



**Earthquake Model Expects**: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second# Terminal 1: Backend (Flask on 127.0.0.1:5000)



**Tsunami Model Expects**: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Secpython src/api/main.py



Note: Tsunami uses abbreviated month/day/hour/minute/second (Mo, Dy, Hr, Mn, Sec)



**Always verify** before modifying payloads:# Terminal 2: Frontend (React dev on localhost:3000)**Backend** (Flask in `src/api/main.py`)**Backend** (Flask in src/api/main.py)

```bash

python src/api/discover_features.pynpm start

```

- Three endpoints: `POST /earthquake`, `/tsunami`, `/forestfire`- Three endpoints: POST /earthquake, /tsunami, /forestfire

### Backend Column Reordering

# Terminal 3: Test backend without UI

The `_predict()` helper in `main.py` automatically reorders DataFrame columns to match `model.feature_names_in_` via fuzzy matching (case-insensitive, substring). This allows frontend flexibility but requires exact feature names in the payload.

python src/api/test_api.py- Each loads a pre-trained scikit-learn model from `src/api/models/`- Each loads a pre-trained scikit-learn model from src/api/models/

### Prediction History

```

All predictions are auto-added to `PredictionContext` when users complete assessments. View in route `/earthquake` or `/tsunami` via `PredictionHistory.js`.

- Core logic: `_predict(model, data)` helper handles DataFrame construction, column reordering, missing feature filling, and numpy to JSON conversion- Core logic: _predict(model, data) helper handles DataFrame construction, column reordering, missing feature filling, and numpyJSON conversion

## Data Flow for Location-Based Predictions

## Critical Patterns - Read This First

```

LocationSearch- Production: `wsgi.py` exposes Flask app for Gunicorn- Production: wsgi.py exposes Flask app for Gunicorn

  ├─ User selects location via map click or coordinate input

  └─ Calls onLocationSelected(lat, lng, name)### Pattern 1: Model Feature Names Are Exact and Case-Sensitive

        ↓

App.js Router

  ├─ Stores location in component state

  └─ Navigates to `/predictions` showing LocationPredictionDashboardCRITICAL: Scikit-learn 1.0+ enforces strict column matching via model.feature_names_in_.

        ↓

LocationPredictionDashboard## Setup & Quick Start## Setup & Quick Start

  ├─ useEffect triggered by [latitude, longitude] dependency

  ├─ Fetches /earthquake with: Latitude, Longitude, Depth(10km), Year/Month/Day/Hour/Minute/SecondRun this whenever you change a form or model:

  ├─ Fetches /tsunami with: Latitude, Longitude, Tsunami Magnitude(6.5), Year/Mo/Dy/Hr/Mn/Sec

  ├─ Sets state: earthquake={0 or 1}, tsunami={0 or 1}```bash

  └─ Renders prediction cards with risk levels

```python src/api/discover_features.py



## Key Files``````powershell```powershell



| Path | Purpose |

|------|---------|

| `src/Front.js` | Landing page |**Earthquake model expects**: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second# Install dependencies# Install dependencies

| `src/Features.js` | Feature cards routing |

| `src/LocationSearch.js` | Map + coordinate input |

| `src/LocationPredictionDashboard.js` | Auto-fetches & displays predictions |

| `src/App.js` | Router, wraps with PredictionProvider |**Tsunami model expects**: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Secpip install -r requirements.txtpip install -r requirements.txt

| `src/PredictionContext.js` | Global prediction history state |

| `src/api/main.py` | Flask endpoints, _predict() helper |

| `src/api/models/` | earthquake_model.joblib, tsunami_model.joblib |

**Earthquake payload** (src/EarthquakePrediction.js):npm installnpm install

## Known Limitations & Future Improvements

```javascript

### Current Limitations

- Depth hardcoded to 10 km (typical crustal depth)const payload = {

- Tsunami magnitude hardcoded to 6.5 (typical tsunami-generating magnitude)

- Models trained on historical data; cannot predict unprecedented events    Latitude: parseFloat(latitude),

- No real-time integration with USGS or other seismic networks

- Predictions use current date/time; cannot forecast future events    Longitude: parseFloat(longitude),# Terminal 1: Backend (Flask on http://127.0.0.1:5000)# Terminal 1: Backend (Flask on http://127.0.0.1:5000)



### Recommended Improvements    Depth: parseFloat(depth),

1. **User Input for Depth/Magnitude**: Add optional advanced settings for users to specify these values

2. **Confidence Scores**: Modify backend to return confidence/probability, not just 0/1    Year: dateObj.getFullYear(),python src/api/main.pypython src/api/main.py

3. **Uncertainty Visualization**: Show model confidence as % or probability ranges

4. **Data Source Attribution**: Link predictions to training data sources    Month: dateObj.getMonth() + 1,

5. **Comparison View**: Allow users to compare multiple locations side-by-side

6. **Map Heat Map**: Show global earthquake/tsunami risk overlay on map    Day: dateObj.getDate(),

7. **Historical Events**: Display nearby historical earthquakes/tsunamis in results

8. **Local Official Links**: Auto-link to local USGS/JMA/BMKG equivalent for selected location    Hour: 12,



## Common Issues & Debugging    Minute: 0,# Terminal 2: Frontend (React dev on http://localhost:3000)# Terminal 2: Frontend (React dev on http://localhost:3000)



**Q: Both predictions always return 0 (low risk)?**    Second: 0

A: Likely missing required features. Run `python src/api/discover_features.py` and verify the payload matches exactly.

};npm startnpm start

**Q: Tsunami predictions fail but earthquake works?**

A: Check that tsunami payload uses abbreviated field names (Mo, Dy, Hr, Mn, Sec not Month/Day/Hour/Minute/Second).```



**Q: Location not updating predictions?**

A: Verify `LocationPredictionDashboard` receives lat/lng via App.js router state. Check browser DevTools Network tab for API errors.

**Tsunami payload** (src/TsunamiPrediction.js) - Note abbreviated names:

**Q: Backend returns 400 error?**

A: Check Flask logs (terminal where you ran main.py). Common issues: wrong feature names, missing required fields, invalid coordinate ranges.```javascript# Terminal 3 (optional): Test backend without UI# Terminal 3 (optional): Test backend without UI



## Environment Variablesconst payload = {



```    Latitude: parseFloat(latitude),python src/api/test_api.pypython src/api/test_api.py

REACT_APP_API_URL=http://localhost:5000  # Backend URL (defaults to localhost:5000 if not set)

```    Longitude: parseFloat(longitude),



## Testing    'Tsunami Magnitude (Iida)': parseFloat(magnitude),````



```bash    Year: dateObj.getFullYear(),

# Backend smoke tests (no UI needed)

python src/api/test_api.py    Mo: dateObj.getMonth() + 1,



# Test specific location:    Dy: dateObj.getDate(),

curl -X POST http://localhost:5000/earthquake \

  -H "Content-Type: application/json" \    Hr: 12,## Critical Patterns - Read This First## Critical Patterns � Read This First

  -d '{"Latitude":40.7128,"Longitude":-74.0060,"Depth":10,"Year":2024,"Month":11,"Day":12,"Hour":0,"Minute":0,"Second":0}'

```    Mn: 0,



## Next Steps for Development    Sec: 0



1. **Add depth/magnitude inputs** in LocationPredictionDashboard (advanced options)};

2. **Display model confidence** in risk cards (requires backend modification)

3. **Add historical earthquake overlay** on map using USGS API```### Pattern 1: Model Feature Names Are Exact and Case-Sensitive### Pattern 1: Model Feature Names Are Exact and Case-Sensitive

4. **Create comparison view** for multiple locations

5. **Add PDF export** of assessment report

6. **Mobile optimization** (currently desktop-focused)

**Backend handling** (src/api/main.py):

- Wraps scalar dicts in list for pandas DataFrame construction

- Reorders columns to match model.feature_names_in_**This is the #1 source of bugs.** Scikit-learn 1.0+ enforces strict column matching via `model.feature_names_in_`.**This is the #1 source of bugs.** Scikit-learn 1.0+ enforces strict column matching via model.feature_names_in_.

- Fills missing features with zeros via fuzzy matching

- Converts numpy scalars using .item() for JSON serialization



### Pattern 2: Shared Prediction History via React ContextRun this whenever you change a form or model:Run this whenever you change a form or model:



All predictions stored in PredictionContext and displayed in PredictionHistory.js on every route.```bash



**Adding to history** (any prediction form):```bashpython src/api/discover_features.py

```javascript

const { addPrediction } = useContext(PredictionContext);python src/api/discover_features.py`

addPrediction('Earthquake', { latitude, longitude, depth, date }, json.prediction);

``````



History structure: Array of { id, type, inputs, result, timestamp }Output example:



PredictionHistory.js renders as scrollable list with color-coded badges, timestamps, and formatted JSON inputs.**Earthquake model expects**: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second```



### Pattern 3: Environment Variable for API URL=== EARTHQUAKE MODEL ===



**Always use**:**Tsunami model expects**: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, SecFeature names: ['Latitude' 'Longitude' 'Depth' 'Year' 'Month' 'Day' 'Hour' 'Minute' 'Second']

```javascript

const backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';

fetch(`${backend}/earthquake`, ...)

```**Earthquake payload** (from `src/EarthquakePrediction.js`):=== TSUNAMI MODEL ===



**Never hardcode** 127.0.0.1:5000. Replace any found in LocationPredictionDashboard.js.```javascriptFeature names: ['Latitude' 'Longitude' 'Tsunami Magnitude (Iida)' 'Year' 'Mo' 'Dy' 'Hr' 'Mn' 'Sec']



### Pattern 4: Windows Requires Disabled Flask Auto-Reloaderconst payload = {`



In src/api/main.py:    Latitude: parseFloat(latitude),

```python

app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)    Longitude: parseFloat(longitude),**Earthquake payload** (from src/EarthquakePrediction.js):

```

    Depth: parseFloat(depth),```javascript

Do not enable auto-reloader - Windows port binding will conflict.

    Year: dateObj.getFullYear(),const payload = {

## Workflows

    Month: dateObj.getMonth() + 1,    Latitude: parseFloat(latitude),

### Add a New Prediction Input Field

    Day: dateObj.getDate(),    Longitude: parseFloat(longitude),

1. Update form component and payload with new field

2. Verify model expects it: python src/api/discover_features.py    Hour: 12,    Depth: parseFloat(depth),

3. If not in feature_names_in_, model must be retrained

4. Test: python src/api/test_api.py    Minute: 0,    Year: dateObj.getFullYear(),



### Retrain a Model    Second: 0    Month: dateObj.getMonth() + 1,  // JS months 0-indexed!



```powershell};    Day: dateObj.getDate(),

python src/api/retrain_models.py --task earthquake --data data/earthquake.csv --outdir src/api/models

``````    Hour: 12,  // Fixed default



**Earthquake CSV**: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second, label    Minute: 0,



**Tsunami CSV**: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Sec, label**Tsunami payload** (from `src/TsunamiPrediction.js`) - Note abbreviated field names (Mo, Dy, Hr, Mn, Sec not Month/Day/Hour/Minute/Second):    Second: 0



After retraining: restart Flask, run discover_features.py to confirm.```javascript};



### Debug a Prediction Failureconst payload = {`



```bash    Latitude: parseFloat(latitude),

python src/api/discover_features.py  # Check model internals

python src/api/test_api.py           # Test backend in isolation    Longitude: parseFloat(longitude),**Tsunami payload** (from src/TsunamiPrediction.js) � Note abbreviated field names:

# Watch Flask logs (terminal where you ran main.py)

# Check browser DevTools Network tab for 400/500 responses    'Tsunami Magnitude (Iida)': parseFloat(magnitude),```javascript

```

    Year: dateObj.getFullYear(),const payload = {

## File Map

    Mo: dateObj.getMonth() + 1,    Latitude: parseFloat(latitude),

| Path | Purpose |

|------|---------|    Dy: dateObj.getDate(),    Longitude: parseFloat(longitude),

| src/api/main.py | Flask app, 3 endpoints, _predict() helper |

| src/api/test_api.py | In-process smoke tests |    Hr: 12,    'Tsunami Magnitude (Iida)': parseFloat(magnitude),

| src/api/discover_features.py | Loads models, prints feature_names_in_ |

| src/api/retrain_models.py | StandardScaler + RandomForest trainer |    Mn: 0,    Year: dateObj.getFullYear(),

| src/PredictionContext.js | React Context for global prediction state |

| src/PredictionHistory.js | Display component for all predictions |    Sec: 0    Mo: dateObj.getMonth() + 1,  // 'Mo' not 'Month'

| src/EarthquakePrediction.js | Form: exact feature names |

| src/TsunamiPrediction.js | Form: abbreviated feature names |};    Dy: dateObj.getDate(),       // 'Dy' not 'Day'

| src/App.js | Router setup, wraps app with PredictionProvider |

| wsgi.py | WSGI entry for Gunicorn (production) |```    Hr: 12,                       // 'Hr' not 'Hour'

| src/api/models/ | Binary artifacts: joblib/pkl files |

    Mn: 0,                        // 'Mn' not 'Minute'

## Before Major Changes, Read

**Backend handling** (in `src/api/main.py`):    Sec: 0                        // 'Sec' not 'Second'

1. Modifying a form payload: src/EarthquakePrediction.js and src/TsunamiPrediction.js

2. Adding endpoints: src/api/main.py (use _predict() pattern, ensure CORS)- Wraps scalar dicts in list for pandas DataFrame construction};

3. Cross-route state: src/PredictionContext.js and src/App.js (wrap Provider at root)

4. Model requirements: src/api/discover_features.py (run it, believe it)- Reorders columns to match `model.feature_names_in_``



## Common Mistakes to Avoid- Fills missing features with zeros via fuzzy matching (case-insensitive, substring)



- Hardcoding 127.0.0.1:5000 instead of process.env.REACT_APP_API_URL- Converts numpy scalars to Python types using `.item()` for JSON serialization**Backend handling** (in src/api/main.py):

- Sending feature names that differ from model.feature_names_in_ (causes always-same-prediction bugs)

- Forgetting to wrap dict payloads in list for pandas DataFrame construction```python

- Enabling Flask auto-reloader on Windows

- Not converting numpy scalars with .item() before JSON serialization### Pattern 2: Shared Prediction History via React Contextdef _predict(model, data):


    df = pd.DataFrame([data])  # Wrap scalar dict

All predictions are stored in `PredictionContext` and displayed in `PredictionHistory.js` on every route.    

    # Reorder columns to match model.feature_names_in_

**Adding to history** (in any prediction form):    if hasattr(model, 'feature_names_in_'):

```javascript        expected = list(model.feature_names_in_)

const { addPrediction } = useContext(PredictionContext);        # Fuzzy match provided columns to expected (case-insensitive, substring)

addPrediction('Earthquake', { latitude, longitude, depth, date }, json.prediction);        # Fill missing with zeros, reorder to expected order

```        df = df[...].rename(...)  # See full implementation in main.py

    

**History structure**: Array of { id, type, inputs, result, timestamp }    pred = model.predict(df)

    return pred[0].item()  # Convert numpy scalar to Python int/float

`PredictionHistory.js` renders this as a scrollable list with color-coded badges, timestamps, and formatted JSON inputs.`



### Pattern 3: Environment Variable for API URL### Pattern 2: Shared Prediction History via React Context



**Always use**:All predictions are stored in PredictionContext and displayed in PredictionHistory.js on every route.

```javascript

const backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';**Adding to history** (in any prediction form):

fetch(`${backend}/earthquake`, ...)```javascript

```import { useContext } from 'react';

import { PredictionContext } from './PredictionContext';

**Never hardcode** `http://127.0.0.1:5000`. Replace any you find in `LocationPredictionDashboard.js`.

function MyForm() {

### Pattern 4: Windows Requires Disabled Flask Auto-Reloader    const { addPrediction } = useContext(PredictionContext);

    

In `src/api/main.py`:    // After receiving result from API:

```python    addPrediction('Earthquake', 

app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)        { latitude, longitude, depth, date },  // inputs object

```        json.prediction  // result scalar

    );

**Do not enable auto-reloader** - Windows port binding will conflict.}

`

## Workflows

**History structure** (in PredictionContext.js):

### Add a New Prediction Input Field```javascript

predictions = [

1. Update form component and payload with new field    { id: timestamp, type: 'Earthquake', inputs: {...}, result: 1, timestamp: '12:34:56' },

2. Verify model expects it: `python src/api/discover_features.py`    { id: timestamp, type: 'Tsunami', inputs: {...}, result: 0, timestamp: '12:35:02' }

3. If not in feature_names_in_, model must be retrained]

4. Test: `python src/api/test_api.py``



### Retrain a ModelPredictionHistory.js renders this as a scrollable list with color-coded badges, timestamps, and formatted JSON inputs.



```powershell### Pattern 3: Environment Variable for API URL

python src/api/retrain_models.py --task earthquake --data data/earthquake.csv --outdir src/api/models

```**Always use**:

```javascript

**Earthquake CSV columns**: Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second, labelconst backend = process.env.REACT_APP_API_URL || 'http://localhost:5000';

fetch(\\/earthquake\, ...)

**Tsunami CSV columns**: Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Sec, label`



After retraining: restart Flask, run discover_features.py to confirm.**Never hardcode** http://127.0.0.1:5000. Replace any you find in LocationPredictionDashboard.js.



### Debug a Prediction Failure### Pattern 4: Windows Requires Disabled Flask Auto-Reloader



```bashIn src/api/main.py:

python src/api/discover_features.py  # Check model internals```python

python src/api/test_api.py           # Test backend in isolationapp.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)

# Watch Flask logs (terminal where you ran main.py)`

# Check browser DevTools Network tab for 400/500 responses

```**Do not enable auto-reloader** � Windows port binding will conflict. This is a platform-specific workaround.



## File Map## Workflows



| Path | Purpose |### Add a New Prediction Input Field

|------|---------|

| src/api/main.py | Flask app, 3 endpoints, _predict() helper |1. Update form component (e.g., src/EarthquakePrediction.js):

| src/api/test_api.py | In-process smoke tests |   ```javascript

| src/api/discover_features.py | Loads models, prints feature_names_in_ |   const [newField, setNewField] = useState('');

| src/api/retrain_models.py | StandardScaler + RandomForest trainer |   // Add input: <input value={newField} onChange={e => setNewField(e.target.value)} />

| src/PredictionContext.js | React Context for global prediction state |   // Add to payload

| src/PredictionHistory.js | Display component for all predictions |   `

| src/EarthquakePrediction.js | Form: exact feature names |

| src/TsunamiPrediction.js | Form: abbreviated feature names |2. Verify model expects it:

| src/App.js | Router setup, wraps app with PredictionProvider |   ```bash

| wsgi.py | WSGI entry for Gunicorn (production) |   python src/api/discover_features.py

| src/api/models/ | Binary artifacts: joblib/pkl files |   # If 'newField' is NOT in feature_names_in_, model must be retrained

   `

## Before Major Changes, Read

3. Test immediately:

1. **Modifying a form payload**: src/EarthquakePrediction.js and src/TsunamiPrediction.js (copy exact feature names)   ```bash

2. **Adding endpoints**: src/api/main.py (use _predict() pattern, ensure CORS)   python src/api/test_api.py

3. **Cross-route state**: src/PredictionContext.js and src/App.js (wrap Provider at root)   `

4. **Model requirements**: src/api/discover_features.py (run it, believe it)

### Retrain a Model

## Common Mistakes to Avoid

Models expect CSV with exact feature columns + label (0 or 1):

- Hardcoding 127.0.0.1:5000 instead of process.env.REACT_APP_API_URL

- Sending feature names that differ from model.feature_names_in_ (causes always-same-prediction bugs)```powershell

- Forgetting to wrap dict payloads in list for pandas DataFrame constructionpython src/api/retrain_models.py --task earthquake --data data/earthquake.csv --outdir src/api/models

- Enabling Flask auto-reloader on Windows`

- Not converting numpy scalars with .item() before JSON serialization

**Earthquake CSV columns** (exact case):
Latitude, Longitude, Depth, Year, Month, Day, Hour, Minute, Second, label

**Tsunami CSV columns**:
Latitude, Longitude, Tsunami Magnitude (Iida), Year, Mo, Dy, Hr, Mn, Sec, label

After retraining: restart Flask, run discover_features.py to confirm.

### Debug a Prediction Failure

```bash
# 1. Check model internals
python src/api/discover_features.py

# 2. Test backend in isolation (no UI, no network)
python src/api/test_api.py

# 3. Watch Flask logs (terminal where you ran main.py)
# 4. Check browser DevTools Network tab for 400/500 responses
`

## File Map

| Path | Purpose |
|------|---------|
| src/api/main.py | Flask app, 3 endpoints, _predict() helper (column reordering, numpy to JSON) |
| src/api/test_api.py | In-process smoke tests for all endpoints |
| src/api/discover_features.py | Loads models, prints feature_names_in_ |
| src/api/retrain_models.py | StandardScaler + RandomForest pipeline trainer |
| src/PredictionContext.js | React Context: { predictions, addPrediction, clearPredictions } |
| src/PredictionHistory.js | Display component (scrollable list, JSON inputs, color badges) |
| src/EarthquakePrediction.js | Form with 5 inputs, constructs payload with exact feature names |
| src/TsunamiPrediction.js | Form with 5 inputs, constructs payload with abbreviated field names |
| src/App.js | Router setup, wraps app with PredictionProvider |
| wsgi.py | WSGI entry for Gunicorn (production) |
| src/api/models/ | Binary artifacts: earthquake_model.joblib, tsunami_model.joblib, forestfiremodel.pkl |

## Before Major Changes, Read

1. **Modifying a form payload**: src/EarthquakePrediction.js and src/TsunamiPrediction.js (copy exact feature names from discover_features.py)
2. **Adding/changing endpoints**: src/api/main.py (use _predict() pattern, ensure CORS enabled)
3. **Cross-route state**: src/PredictionContext.js and src/App.js (wrap Provider at root)
4. **Model requirements**: src/api/discover_features.py (run it, believe it)

## Common Mistakes to Avoid

- Do not hardcode http://127.0.0.1:5000 instead of using process.env.REACT_APP_API_URL
- Do not send feature names that differ from model.feature_names_in_ (causes silent failures / always-same-prediction bugs)
- Do not forget to wrap dict payloads in a list for pandas DataFrame construction
- Do not enable Flask auto-reloader on Windows (port binding conflict)
- Do not forget to convert numpy scalars (use .item()) before JSON serialization
