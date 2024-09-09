import os
import sys
import joblib
import pandas as pd
from django.conf import settings

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fplmate_backend.settings')
import django
django.setup()

def load_model(position):
    model_path = os.path.join(settings.BASE_DIR, 'models', f'{position.lower()}_model.joblib')
    if os.path.exists(model_path):
        print(f"Loading model for position: {position} from {model_path}")
        model = joblib.load(model_path)
        return model
    else:
        print(f"No model found for position: {position}")
        return None

def test_model(position, sample_data):
    model = load_model(position)
    if model:
        features = ['now_cost', 'assists', 'goals_scored', 'clean_sheets', 'minutes', 'bps', 'saves', 'influence', 'creativity', 'threat', 'ict_index']
        df = pd.DataFrame([sample_data], columns=features)
        prediction = model.predict(df)
        print(f"Prediction for position {position}: {prediction[0]}")
    else:
        print(f"Unable to test model for position: {position}")

# Example test data (adjust as needed)
sample_data_fwd = {
    'now_cost': 10,
    'assists': 5,
    'goals_scored': 3,
    'clean_sheets': 1,
    'minutes': 80,
    'bps': 30,
    'saves': 0,
    'influence': 20,
    'creativity': 15,
    'threat': 25,
    'ict_index': 60
}

sample_data_mid = {
    'now_cost': 8,
    'assists': 6,
    'goals_scored': 2,
    'clean_sheets': 2,
    'minutes': 85,
    'bps': 35,
    'saves': 0,
    'influence': 25,
    'creativity': 20,
    'threat': 30,
    'ict_index': 70
}

# Test each model
test_model('FWD', sample_data_fwd)
test_model('MID', sample_data_mid)
