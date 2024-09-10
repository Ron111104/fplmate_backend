import os
import sys
import random
import pandas as pd
import joblib
from django.conf import settings

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fplmate_backend.settings')
import django
django.setup()

# Generate random test data for each player attribute
def generate_test_data(position, num_samples=20):
    """Generate random data for testing based on position."""
    data = []
    for _ in range(num_samples):
        player_data = {
            'now_cost': random.randint(45, 120),
            'assists': random.randint(0, 15),
            'goals_scored': random.randint(0, 25),
            'clean_sheets': random.randint(0, 20) if position in ['DEF', 'GKP'] else 0,
            'minutes': random.randint(500, 3000),
            'bps': random.randint(100, 500),
            'saves': random.randint(0, 120) if position == 'GKP' else 0,
            'influence': random.uniform(0, 200),
            'creativity': random.uniform(0, 200),
            'threat': random.uniform(0, 200),
            'ict_index': random.uniform(0, 600),
            'transfers_in_event': random.randint(0, 10000),
            'expected_goals': random.uniform(0, 20),
            'expected_assists': random.uniform(0, 10),
            'expected_goal_involvements': random.uniform(0, 30),
            'form': random.uniform(0, 10),
            'total_points': random.randint(10, 250)  # Not needed for prediction but useful for generating realistic data
        }
        data.append(player_data)
    return pd.DataFrame(data)

# Load the trained model and predict the ratings
def load_model_and_predict(position, test_data):
    """Load the trained model and make predictions on the test data."""
    model_path = os.path.join(settings.BASE_DIR, 'models', f'{position.lower()}_model.joblib')
    
    if not os.path.exists(model_path):
        print(f"Model for {position} not found at {model_path}. Skipping...")
        return None
    
    # Load the trained model
    model = joblib.load(model_path)
    print(f"Loaded model for {position}")

    # Prepare features for prediction
    features = [
        'now_cost', 'assists', 'goals_scored', 'clean_sheets', 
        'minutes', 'bps', 'saves', 'influence', 'creativity', 
        'threat', 'ict_index', 'transfers_in_event', 'expected_goals',
        'expected_assists', 'expected_goal_involvements', 'form'
    ]
    
    available_features = [feat for feat in features if feat in test_data.columns]
    
    X_test = test_data[available_features]
    
    # Make predictions (ratings from 0 to 100)
    predictions = model.predict(X_test)
    predictions = [max(0, min(100, round(pred))) for pred in predictions]  # Clamp ratings between 0 and 100
    
    # Return predictions
    return predictions

def test_models():
    """Test the trained models using randomly generated data."""
    print("Starting model testing...")
    
    positions = ['FWD', 'MID', 'DEF', 'GKP']
    
    for position in positions:
        print(f"\nGenerating random test data for {position}...")
        
        # Generate test data for this position
        test_data = generate_test_data(position, num_samples=20)
        
        # Load the model and predict using the test data
        predictions = load_model_and_predict(position, test_data)
        
        if predictions is not None:
            print(f"Predictions (ratings) for {position}: {predictions}")
    
    print("Model testing completed.")

if __name__ == "__main__":
    test_models()
