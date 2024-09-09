import os
import pandas as pd
import joblib
from django.conf import settings
import numpy as np

# Set up Django environment
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fplmate_backend.settings')
import django
django.setup()

def predict_ratings(input_csv, output_csv):
    print(f"Predicting ratings for {input_csv}...")

    # Load the dataset
    dataset_path = os.path.join(settings.BASE_DIR, input_csv)
    print(f"Loading dataset from {dataset_path}")
    data = pd.read_csv(dataset_path)
    print("Dataset loaded successfully.")

    # Add a new feature to reduce the weightage of `minutes` for high values
    data['adjusted_minutes'] = data['minutes'].apply(lambda x: x if x <= 1000 else 1000 + (x - 1000) * 0.1)
    
    # Define possible features
    possible_features = [
        'now_cost', 'assists', 'goals_scored', 'clean_sheets', 
        'adjusted_minutes', 'bps', 'saves', 'influence', 'creativity', 
        'threat', 'ict_index', 'transfers_in_event', 'expected_goals',
        'expected_assists', 'expected_goal_involvements', 'form'
    ]
    
    # Load models
    positions = ['FWD', 'MID', 'DEF', 'GKP']
    models = {}
    feature_names = {}
    
    for position in positions:
        model_path = os.path.join(settings.BASE_DIR, 'models', f'{position.lower()}_model.joblib')
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            models[position] = model
            feature_names[position] = model.feature_names_in_
        else:
            print(f"No model found for position: {position}")

    # Predict ratings
    predictions = []
    
    for position, model in models.items():
        subset = data[data['position'] == position]
        if subset.empty:
            continue

        # Select features available in the dataset
        available_features = [f for f in possible_features if f in subset.columns]
        
        # Ensure all features required by the model are present
        # Add missing features with default values
        for feature in set(feature_names[position]) - set(available_features):
            subset.loc[:, feature] = 0

        # Ensure no extra features are included
        X = subset[feature_names[position]]
        
        # Predict ratings
        subset = subset.copy()
        subset.loc[:, 'predicted_rating'] = model.predict(X)
        
        # Ensure ratings are integers
        subset['predicted_rating'] = subset['predicted_rating'].apply(lambda x: int(round(x)))
        predictions.append(subset[['name', 'position', 'now_cost', 'predicted_rating']])

    if predictions:
        all_predictions = pd.concat(predictions)
        output_path = os.path.join(settings.BASE_DIR, output_csv)
        all_predictions.to_csv(output_path, index=False)
        print(f"Ratings predicted and saved to {output_path}")
    else:
        print("No predictions made. Please check your data and models.")

if __name__ == "__main__":
    seasons = ['2020-21', '2021-22', '2022-23', '2023-24']

    for season in seasons:
        input_csv = f'data/players_{season}.csv'  # Path to the input CSV file
        output_csv = f'data/predicted_ratings_{season}.csv'  # Path to save the output CSV file
        predict_ratings(input_csv, output_csv)
