# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

## Run on a new system (Windows PowerShell)

Follow these steps to set up and run the project from a fresh machine. The instructions assume Windows PowerShell and Python 3.10+ (this project was developed on Python 3.14). Adjust commands for macOS/Linux as needed.

1) Clone the repository

```powershell
git clone <your-repo-url> Disaster-Prediction-master
cd Disaster-Prediction-master
```

2) Set up Python environment and install dependencies

```powershell
# Create and activate virtualenv (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install Python deps
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Install frontend dependencies

```powershell
cd .\src\..\
npm install
cd -
```

4) Ensure model artifacts exist

The backend expects model artifacts under `src/api/models/`:
- `earthquake_model.joblib`
- `tsunami_model.joblib`

If these files are missing, either run the training script(s) or ask the maintainer to provide the `joblib` files.

To retrain and produce models locally (optional):

```powershell
python src/api/retrain_models_v2.py --tsunami-csv data/tsunami_cleaned.csv --earthquake-csv data/earthquake_synthetic.csv --outdir src/api/models
```

5) Run backend (Flask)

```powershell
# From repository root
python src/api/main.py

# The backend will listen on http://127.0.0.1:5000 by default
```

6) Run frontend (React)

```powershell
npm start
# Visit http://localhost:3000
```

7) Generate PDF project report (optional)

This repo includes a script that converts the detailed markdown report to a PDF (`project report.pdf`). Run it after installing Python deps:

```powershell
python scripts/generate_project_report.py
```

8) Environment variables

You can override the backend/frontend defaults using environment variables:
- `TSUNAMI_HISTORICAL_RADIUS_KM` — radius in km for historical tsunami proximity (default 75.0)
- `REACT_APP_API_URL` — frontend API base URL (e.g. `http://127.0.0.1:5000`)

9) Pushing to GitHub (if you want to upload this repo)

Git must be installed locally to push. If you see `git` not found, install Git for Windows first: https://git-scm.com/download/win

Commands to publish (run from repo root):

```powershell
# Initialize (if not a git repo)
git init
git add .
git commit -m "Project: cleaned, documented, ready for deployment"

# Add remote and push (replace <url>)
git remote add origin <your-remote-repo-url>
git branch -M main
git push -u origin main
```

If pushing from CI or an automated environment, prefer using a deploy key, GitHub Actions, or a personal access token stored in secrets.

Troubleshooting
- If `git` is not installed, install it and re-run the push commands.
- If push fails due to authentication, configure credentials or use an SSH key.

If you want, I can prepare a small `deploy.sh`/PowerShell script to automate these steps — tell me your preferred remote URL or whether you want instructions only.
