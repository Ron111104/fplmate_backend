import joblib
import numpy as np
from django.http import JsonResponse
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'trained_models', 'fpl_linear_model.pkl')

# Load the trained model
model = joblib.load(model_path)

# List of expected features for input
expected_features = [
    "minutes", "goals_scored", "assists", "clean_sheets", 
    "yellow_cards", "red_cards", "bonus", "saves", "price"
]

# Max price values by player position
max_price_by_position = {
    1: 5.8,   # Goalkeeper
    2: 7.3,   # Defender
    3: 13.5,  # Midfielder
    4: 15.3   # Forward
}

def calculate_points(data):
    points = 0
    points += data['minutes'] // 60
    if data['element_type'] == 1:  # Goalkeeper
        points += (6 * data['goals_scored']) + (4 * data['clean_sheets']) + (data['saves'] // 3)
    elif data['element_type'] == 2:  # Defender
        points += (6 * data['goals_scored']) + (4 * data['clean_sheets'])
    elif data['element_type'] == 3:  # Midfielder
        points += (5 * data['goals_scored']) + (3 * data['assists']) + (1 * data['clean_sheets'])
    elif data['element_type'] == 4:  # Forward
        points += (4 * data['goals_scored']) + (3 * data['assists'])
    points += data['assists'] + data['bonus'] - data['yellow_cards'] - (2 * data['red_cards'])
    return points

def predict_rating(request):
    if request.method == 'POST':
        try:
            # Parse the JSON input from the request body
            data = json.loads(request.body)
            print(data)
            # Ensure that the request contains the expected features
            if all(feature in data for feature in expected_features):
                # Prepare the input data and reshape it to a 2D array (1 sample, 8 features)
                input_data = np.array([[data[feature] for feature in expected_features if feature != 'price']])
                
                # Predict rating using the trained model
                predicted_rating = model.predict(input_data)[0]

                # Round up to the nearest integer
                predicted_rating = int(np.ceil(predicted_rating))
                
                # Get the price and element_type (position) for normalization
                price = data['price']
                element_type = data['element_type']
                
                # Apply normalization if the position is valid
                if element_type in max_price_by_position:
                    max_price = max_price_by_position[element_type]
                    normalized_rating = predicted_rating * 0.9 + 0.1 * predicted_rating * (max_price / price)
                else:
                    normalized_rating = predicted_rating  # Fallback if element_type is invalid
                
                # Return the normalized prediction result as a JSON response
                return JsonResponse({'predicted_rating': round(normalized_rating, 2)}, status=200)

            else:
                return JsonResponse({'error': 'Missing required input features'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
