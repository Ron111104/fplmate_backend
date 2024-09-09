import os
import sys
import pandas as pd
import joblib
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fplmate_backend.settings')
import django
django.setup()

def train_and_save_models():
    print("Starting the training and saving process...")

    # Combine datasets from all seasons
    seasons = ['2020-21', '2021-22', '2022-23', '2023-24']
    all_data = []
    
    for season in seasons:
        dataset_path = os.path.join(settings.BASE_DIR, f'data/players_{season}.csv')
        print(f"Loading dataset from {dataset_path}")
        data = pd.read_csv(dataset_path)
        all_data.append(data)
    
    # Concatenate all season data into a single DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)
    print("Combined dataset loaded successfully.")

    # Positions to train models for
    positions = ['FWD', 'MID', 'DEF', 'GKP']

    for position in positions:
        print(f"\nTraining model for position: {position}")

        # Filter data based on position
        subset = combined_data[combined_data['position'] == position]
        if subset.empty:
            print(f"No data available for position: {position}")
            continue
        
        # Features and target variable
        all_features = [
            'now_cost', 'assists', 'goals_scored', 'clean_sheets', 
            'minutes', 'bps', 'saves', 'influence', 'creativity', 
            'threat', 'ict_index', 'transfers_in_event', 'expected_goals',
            'expected_assists', 'expected_goal_involvements', 'form'
        ]
        
        # Select only available features
        available_features = [feat for feat in all_features if feat in subset.columns]
        
        if not available_features:
            print(f"No usable features for position {position}. Skipping model training.")
            continue
        
        X = subset[available_features]
        y = subset['total_points']

        # Handle the weighting of minutes
        X['minutes'] = X['minutes'].apply(lambda x: x if x <= 1000 else 1000)
        
        # Split the data
        print(f"Splitting data for position: {position}")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model with the available features
        print(f"Training model for position: {position} with features: {available_features}")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        print(f"Model training completed for position: {position}")

        # Save the model
        model_path = os.path.join(settings.BASE_DIR, 'models', f'{position.lower()}_model.joblib')
        print(f"Saving model to {model_path}")
        joblib.dump(model, model_path)
        print(f"Model for position {position} saved successfully.")

    print("All models trained and saved successfully.")

# Run the function to train and save models
if __name__ == "__main__":
    train_and_save_models()
