# ai_analyzer.py
import main
import joblib
from datetime import datetime, timezone
import pandas as pd

# Load the trained model from the file
try:
    model = joblib.load('codesentinel_model.pkl')
except FileNotFoundError:
    print("Error: codesentinel_model.pkl not found. Make sure you've downloaded it.")
    model = None

def run_ai_analysis(package_name):
    """
    Gathers live data, formats it, and gets a prediction from the AI model.
    """
    if not model:
        return {"error": "AI model not loaded."}

    # 1. Gather all the raw data using our existing functions
    pypi_data = main.get_package_data(package_name)
    if not pypi_data:
        return {"error": f"Could not find package '{package_name}' on PyPI."}
    
    info = pypi_data.get('info', {})
    releases = pypi_data.get('releases', {})
    version = info.get('version')

    # 2. Convert raw data into the numeric features our model expects
    features = {}
    features['has_author'] = 1 if info.get('author') else 0
    features['has_homepage'] = 1 if info.get('home_page') else 0
    features['num_versions'] = len(releases)

    # Get package age
    if releases:
        all_upload_times = [datetime.fromisoformat(file_info.get('upload_time_iso_8601')) for v in releases.values() for file_info in v if file_info.get('upload_time_iso_8601')]
        if all_upload_times:
            features['package_age_days'] = (datetime.now(timezone.utc) - min(all_upload_times)).days
        else:
            features['package_age_days'] = 0
    else:
        features['package_age_days'] = 0

    # Get GitHub features
    github_username = main.extract_github_username(pypi_data)
    if github_username:
        github_info = main.get_github_user_info(github_username)
        if github_info:
            features['github_followers'] = github_info.get('followers', 0)
            created_at_date = datetime.fromisoformat(github_info.get('created_at').replace('Z', '+00:00'))
            features['github_account_age_days'] = (datetime.now(timezone.utc) - created_at_date).days
        else: # Default values if GitHub user not found
            features['github_followers'] = 0
            features['github_account_age_days'] = 0
    else: # Default values if no GitHub repo found
        features['github_followers'] = 0
        features['github_account_age_days'] = 0

    # Get dangerous code feature
    code_findings = main.analyze_source_code(package_name, version)
    features['has_dangerous_code'] = 1 if code_findings else 0

    # 3. Get a prediction from the AI model
    # We need to format the features into a DataFrame in the correct order
    feature_order = [
        'has_author', 'has_homepage', 'github_followers',
        'github_account_age_days', 'package_age_days', 'num_versions',
        'has_dangerous_code'
    ]
    live_features_df = pd.DataFrame([features], columns=feature_order)

    prediction = model.predict(live_features_df)[0] # Get the 0 or 1 prediction
    probabilities = model.predict_proba(live_features_df)[0] # Get the confidence scores

    return {
        "package_name": package_name,
        "features": features,
        "prediction": int(prediction), # 0 for Safe, 1 for Risky
        "confidence": {
            "safe": round(probabilities[0] * 100, 2),
            "risky": round(probabilities[1] * 100, 2)
        }
    }