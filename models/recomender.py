import os
import pandas as pd
from collections import Counter
from django.http import JsonResponse
from django.views import View

# Base directory for file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def normalize_name(name):
    """Normalize the name to remove special characters."""
    return ''.join(c for c in name if c.isalnum() or c in [' ', '_'])


def load_player_data(players_dir, raw_data_path):
    """Load and merge all player data from CSV files."""
    raw_stats_df = pd.read_csv(raw_data_path, usecols=['element_type', 'team', 'second_name', 'first_name', 'id'])
    all_player_data = pd.DataFrame()

    for player_folder in os.scandir(players_dir):
        if player_folder.is_dir():
            player_name, player_id = player_folder.name.rsplit('_', 1)
            csv_file_path = os.path.join(player_folder, 'gw.csv')

            # Include all required columns from gw.csv
            player_gw_data = pd.read_csv(csv_file_path, usecols=[ 
                'total_points', 'value', 'round', 'minutes', 'starts', 'selected',
                'goals_scored', 'assists', 'expected_goal_involvements', 'threat',
                'expected_goals_conceded', 'goals_conceded', 'clean_sheets'
            ])
            player_gw_data['id'] = int(player_id)
            player_details = raw_stats_df[raw_stats_df['id'] == int(player_id)].iloc[0]

            for col in player_details.index:
                player_gw_data[col] = player_details[col]

            all_player_data = pd.concat([all_player_data, player_gw_data], ignore_index=True)

    all_player_data["element_type"] = all_player_data["element_type"].map({1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'})
    return all_player_data


def calculate_player_stats(player_data, element_type):
    """Calculate specific stats for a player based on their position."""
    stats = {
        'minutes_played': int(player_data['minutes'].sum()),
        'total_starts': int(player_data['starts'].sum()),
        'avg_selected': round(int(player_data['selected'].mean())),
        'goals_scored': int(player_data['goals_scored'].sum()),
        'assists': int(player_data['assists'].sum()),
    }

    if element_type in ['MID', 'FWD']:
        stats.update({
            'total_xgi': round(float(player_data['expected_goal_involvements'].sum()), 2),
            'avg_threat': round(float(player_data['threat'].mean()), 2)
        })
    
    if element_type in ['DEF', 'GK']:
        stats.update({
            'total_xgc': round(float(player_data['expected_goals_conceded'].sum()), 2),
            'goals_conceded': int(player_data['goals_conceded'].sum()),
            'clean_sheets': int(player_data['clean_sheets'].sum())
        })

    return stats


def prepare_latest_data(all_data_df):
    """Prepare the latest data with form calculations and additional stats."""
    game_week = all_data_df['round'].max()
    recent_weeks = all_data_df['round'] > (game_week - 5)
    
    # Calculate form points
    form_data = (all_data_df[recent_weeks]
                .groupby('id')['total_points']
                .mean()
                .reset_index()
                .rename(columns={'total_points': 'form_points'}))

    # Get latest gameweek data
    latest_data = all_data_df[all_data_df['round'] == game_week].copy()
    latest_data = latest_data.merge(form_data, on='id', how='left')
    latest_data['average_total_points'] = round(latest_data['form_points'].fillna(latest_data['total_points']), 2)
    latest_data = latest_data.drop(columns=['form_points'])

    # Calculate additional stats for each player
    player_stats = []
    for _, player in latest_data.iterrows():
        player_recent_data = all_data_df[ 
            (all_data_df['id'] == player['id']) & 
            (all_data_df['round'] > game_week - 6)
        ]
        stats = calculate_player_stats(player_recent_data, player['element_type'])
        stats['id'] = player['id']
        player_stats.append(stats)

    # Merge stats with latest data
    player_stats_df = pd.DataFrame(player_stats)
    latest_data = latest_data.merge(player_stats_df, on='id', how='left')

    return latest_data


def select_best_players_for_position(position, count, max_players_per_team, max_spend, players_df, 
                                   current_players, current_spend, current_teams):
    position_players = players_df[players_df['element_type'] == position].copy()
    current_player_ids = [player['id'] for player in current_players]
    current_teams = current_teams.copy()
    position_players['points_per_value'] = position_players['average_total_points'] / position_players['value']
    position_players = position_players.sort_values(by='points_per_value', ascending=False)
    selected_players = []

    while count > 0 and not position_players.empty:
        player = position_players.iloc[0]
        team_id = player['team']
        player_value = player['value']

        if (player['id'] not in current_player_ids and 
            current_teams.get(team_id, 0) < max_players_per_team and 
            current_spend + player_value <= max_spend):

            player_dict = player.to_dict()
            selected_players.append(player_dict)
            current_spend += player_value
            current_teams[team_id] = current_teams.get(team_id, 0) + 1
            current_player_ids.append(player['id'])
            count -= 1

        position_players = position_players[position_players['id'] != player['id']]

    return selected_players


def select_best_team(team_structure, max_players_per_team, max_spend, players_df):
    total_spend = 0
    team_counts = Counter()
    selected_players = []

    for position, count in team_structure.items():
        players = select_best_players_for_position(
            position, count, max_players_per_team, max_spend, 
            players_df, selected_players, total_spend, team_counts
        )

        for player in players:
            total_spend += player['value']
            team_counts[player['team']] += 1
            selected_players.append(player)

    return pd.DataFrame(selected_players)


def clean_column_names(team_df):
    """Clean and rename columns to be more user-friendly."""
    columns_to_drop = [
        'assists_x', 'clean_sheets_x', 'expected_goal_involvements',
        'expected_goals_conceded', 'goals_conceded_x', 'goals_scored_x',
        'minutes', 'round', 'selected', 'starts'
    ]

    # Basic info column mappings
    column_mapping = {
        'first_name': 'firstName',
        'second_name': 'lastName',
        'element_type': 'position',
        'value': 'price',
        'team': 'teamId',
        'total_points': 'Points',
        'average_total_points': 'Avg Points',
        'minutes_played': 'Minutes',
        'total_starts': 'Starts',
        'avg_selected': 'Ownership',
        'goals_scored_y': 'Goals',
        'assists_y': 'Assists',
        'clean_sheets_y': 'CleanSheets',
        'goals_conceded_y': 'GoalsConceded',
        'total_xgi': ' XGI',
        'total_xgc': 'XGC',
        'threat': 'threat',
        'avg_threat': 'Threat'
    }

    team_df.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    cleaned_df = team_df.copy()
    cleaned_df.rename(columns=column_mapping, inplace=True)

    columns_to_drop_other = ['points_per_value']
    cleaned_df.drop(columns=columns_to_drop_other, errors='ignore', inplace=True)

    # Round numeric columns
    numeric_columns = cleaned_df.select_dtypes(include=['float64']).columns
    cleaned_df[numeric_columns] = cleaned_df[numeric_columns].round(2)

    return cleaned_df

def load_teams_data(teams_path):
    """Load team data and create a mapping of teamId to team name."""
    teams_df = pd.read_csv(teams_path, usecols=['id', 'name'])
    team_mapping = dict(zip(teams_df['id'], teams_df['name']))
    return team_mapping

# Constants
MAX_PLAYERS_PER_TEAM = 3
MAX_SPEND = 1000
TEAM_STRUCTURE = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}


class RecommendTeamView(View):
    def get(self, request):
        players_dir = os.path.join(BASE_DIR, 'data', 'Fantasy-Premier-League/data/2024-25/players/')
        raw_data_path = os.path.join(BASE_DIR, 'data', 'Fantasy-Premier-League/data/2024-25/players_raw.csv')
        teams_path = os.path.join(BASE_DIR, 'data', 'Fantasy-Premier-League/data/2024-25/teams.csv')
        
        try:
            # Load and prepare data
            all_data = load_player_data(players_dir, raw_data_path)
            latest_data = prepare_latest_data(all_data)
            team_mapping = load_teams_data(teams_path)
            # Generate best team
            team_df = select_best_team(TEAM_STRUCTURE, MAX_PLAYERS_PER_TEAM, MAX_SPEND, latest_data)
            total_points = round(float(team_df['average_total_points'].sum()), 2)
            total_spend = round(float(team_df['value'].sum()), 2)
            cleaned_team_df = clean_column_names(team_df)
            cleaned_team_df = cleaned_team_df.fillna(0)
            cleaned_team_df['teamName'] = cleaned_team_df['teamId'].map(team_mapping)
            cleaned_team_df.drop(columns=['teamId'], inplace=True)
            return JsonResponse({'team': cleaned_team_df.to_dict(orient='records'),
                                 'total_points': total_points,
                                 'total_spend': total_spend})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
