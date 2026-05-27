"""
Core logic for Ultimate Frisbee Power Rankings using OpenSkill.
Handles player ratings, match recording, and data persistence.
"""
import csv
import math
import os
from typing import List, Dict, Tuple

from openskill.models import PlackettLuce, PlackettLuceRating


# Constants
DEFAULT_MU = 25.0
DEFAULT_SIGMA = 8.33
PLAYERS_FILE = 'players.csv'
MATCHES_FILE = 'matches.csv'

# USR (Ultimate Skill Rating) display scale
# We keep OpenSkill internal values (mu/sigma) but display a 1000-centered rating.
# Scale chosen so that sigma ~8.33 maps to ~333 points of uncertainty.
USR_BASE = 1000.0
USR_POINTS_PER_MU = 40.0


def mu_to_usr(mu: float) -> float:
    """Convert OpenSkill mu to USR points."""
    return USR_BASE + (mu - DEFAULT_MU) * USR_POINTS_PER_MU


def sigma_to_usr_sigma(sigma: float) -> float:
    """Convert OpenSkill sigma to USR-point uncertainty."""
    return sigma * USR_POINTS_PER_MU


def conservative_usr(mu: float, sigma: float) -> float:
    """Conservative USR rating: (mu - 3*sigma) mapped into USR scale."""
    return mu_to_usr(mu - 3.0 * sigma)


def parse_team(team_str: str) -> List[str]:
    return [p.strip() for p in (team_str or "").split(",") if p.strip()]


def get_player_match_history(player_name: str) -> List[Dict]:
    """
    Return chronological match history entries for a player.
    Each entry includes opponent team, result, and score.
    """
    history: List[Dict] = []
    for idx, match in enumerate(load_matches(), start=1):
        team_a = parse_team(match.get("team_a", ""))
        team_b = parse_team(match.get("team_b", ""))
        try:
            score_a = int(match.get("score_a", 0))
            score_b = int(match.get("score_b", 0))
        except ValueError:
            score_a, score_b = 0, 0

        in_a = player_name in team_a
        in_b = player_name in team_b
        if not (in_a or in_b):
            continue

        if score_a == score_b:
            result = "T"
        elif (in_a and score_a > score_b) or (in_b and score_b > score_a):
            result = "W"
        else:
            result = "L"

        entry = {
            "Game #": idx,
            "Team": "A" if in_a else "B",
            "Result": result,
            "Score For": score_a if in_a else score_b,
            "Score Against": score_b if in_a else score_a,
            "Margin": abs(score_a - score_b),
            "Teammates": ", ".join([p for p in (team_a if in_a else team_b) if p != player_name]),
            "Opponents": ", ".join(team_b if in_a else team_a),
        }
        history.append(entry)
    return history


def load_players() -> Dict[str, PlackettLuceRating]:
    """Load players from CSV file. Returns dict mapping name -> PlackettLuceRating."""
    players = {}
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                mu = float(row['mu'])
                sigma = float(row['sigma'])
                players[name] = PlackettLuceRating(mu=mu, sigma=sigma)
    return players


def save_players(players: Dict[str, PlackettLuceRating]):
    """Save players to CSV file."""
    with open(PLAYERS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'mu', 'sigma'])
        for name, rating in sorted(players.items()):
            writer.writerow([name, rating.mu, rating.sigma])


def load_matches() -> List[Dict]:
    """Load all matches from CSV file."""
    matches = []
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                matches.append(row)
    return matches


def save_match(team_a: List[str], team_b: List[str], score_a: int, score_b: int):
    """Append a match to the matches CSV file."""
    file_exists = os.path.exists(MATCHES_FILE)
    
    with open(MATCHES_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['team_a', 'team_b', 'score_a', 'score_b']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'team_a': ','.join(team_a),
            'team_b': ','.join(team_b),
            'score_a': score_a,
            'score_b': score_b
        })


def add_player(name: str, players: Dict[str, PlackettLuceRating] = None):
    """Add a new player to the system."""
    if players is None:
        players = load_players()
    
    if name not in players:
        players[name] = PlackettLuceRating(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA)
        save_players(players)
    return players


def calculate_mov_multiplier(score_a: int, score_b: int) -> float:
    """
    Calculate Margin of Victory multiplier.
    multiplier = 1 + (ln(abs(score_a - score_b) + 1) / ln(15))
    """
    margin = abs(score_a - score_b)
    if margin == 0:
        return 1.0
    return 1.0 + (math.log(margin + 1) / math.log(15))


def record_game(team_a: List[str], team_b: List[str], score_a: int, score_b: int, 
                players: Dict[str, PlackettLuceRating] = None) -> Dict[str, PlackettLuceRating]:
    """
    Record a game and update player ratings using OpenSkill with MoV multiplier.
    
    The MoV multiplier is applied only to the change in Mu (delta_mu) for each player.
    """
    if players is None:
        players = load_players()
    
    # Ensure all players exist
    for name in team_a + team_b:
        if name not in players:
            players[name] = PlackettLuceRating(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA)
    
    # Store original ratings
    original_ratings = {name: PlackettLuceRating(mu=players[name].mu, sigma=players[name].sigma) 
                       for name in team_a + team_b}
    
    # Create model instance
    model = PlackettLuce()
    
    # Prepare teams for OpenSkill
    team_a_ratings = [players[name] for name in team_a]
    team_b_ratings = [players[name] for name in team_b]
    
    # Determine winner based on score and prepare teams for OpenSkill
    # OpenSkill expects teams in order: [winner, loser]
    if score_a > score_b:
        # Team A wins
        teams = [team_a_ratings, team_b_ratings]
        team_a_is_winner = True
    elif score_b > score_a:
        # Team B wins
        teams = [team_b_ratings, team_a_ratings]
        team_a_is_winner = False
    else:
        # Tie - not supported by Plackett-Luce, treat as Team A win for now
        teams = [team_a_ratings, team_b_ratings]
        team_a_is_winner = True
    
    # Calculate new ratings using OpenSkill
    new_ratings = model.rate(teams)
    
    # Apply MoV multiplier to delta_mu only
    mov_multiplier = calculate_mov_multiplier(score_a, score_b)
    
    # Update player ratings with MoV-adjusted deltas
    # Map ratings back to original team order
    if team_a_is_winner:
        # Team A is winner (index 0), Team B is loser (index 1)
        for i, name in enumerate(team_a):
            original = original_ratings[name]
            updated = new_ratings[0][i]
            delta_mu = updated.mu - original.mu
            adjusted_delta_mu = delta_mu * mov_multiplier
            players[name] = PlackettLuceRating(
                mu=original.mu + adjusted_delta_mu,
                sigma=updated.sigma
            )
        
        for i, name in enumerate(team_b):
            original = original_ratings[name]
            updated = new_ratings[1][i]
            delta_mu = updated.mu - original.mu
            adjusted_delta_mu = delta_mu * mov_multiplier
            players[name] = PlackettLuceRating(
                mu=original.mu + adjusted_delta_mu,
                sigma=updated.sigma
            )
    else:
        # Team B is winner (index 0), Team A is loser (index 1)
        for i, name in enumerate(team_b):
            original = original_ratings[name]
            updated = new_ratings[0][i]
            delta_mu = updated.mu - original.mu
            adjusted_delta_mu = delta_mu * mov_multiplier
            players[name] = PlackettLuceRating(
                mu=original.mu + adjusted_delta_mu,
                sigma=updated.sigma
            )
        
        for i, name in enumerate(team_a):
            original = original_ratings[name]
            updated = new_ratings[1][i]
            delta_mu = updated.mu - original.mu
            adjusted_delta_mu = delta_mu * mov_multiplier
            players[name] = PlackettLuceRating(
                mu=original.mu + adjusted_delta_mu,
                sigma=updated.sigma
            )
    
    return players


def recalculate_all_ratings():
    """
    Recalculate all player ratings from scratch by processing all matches.
    Used for undo functionality to ensure data integrity.
    """
    # Reset all players to default ratings
    players = {}
    
    # Get all player names from matches
    matches = load_matches()
    all_players = set()
    for match in matches:
        team_a = match['team_a'].split(',')
        team_b = match['team_b'].split(',')
        all_players.update(team_a + team_b)
    
    # Initialize all players
    for name in all_players:
        players[name] = PlackettLuceRating(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA)
    
    # Process all matches in order
    for match in matches:
        team_a = match['team_a'].split(',')
        team_b = match['team_b'].split(',')
        score_a = int(match['score_a'])
        score_b = int(match['score_b'])
        players = record_game(team_a, team_b, score_a, score_b, players)
    
    # Save updated ratings
    save_players(players)
    return players


def get_player_records(players: Dict[str, PlackettLuceRating]) -> Dict[str, Tuple[int, int]]:
    """Calculate win/loss records for each player from match history."""
    records = {name: [0, 0] for name in players.keys()}
    matches = load_matches()
    
    for match in matches:
        team_a = match['team_a'].split(',')
        team_b = match['team_b'].split(',')
        score_a = int(match['score_a'])
        score_b = int(match['score_b'])
        
        if score_a > score_b:
            for name in team_a:
                if name in records:
                    records[name][0] += 1
            for name in team_b:
                if name in records:
                    records[name][1] += 1
        elif score_b > score_a:
            for name in team_a:
                if name in records:
                    records[name][1] += 1
            for name in team_b:
                if name in records:
                    records[name][0] += 1
    
    return {name: (wins, losses) for name, (wins, losses) in records.items()}


def delete_last_match():
    """Delete the last match from matches.csv."""
    matches = load_matches()
    if matches:
        matches.pop()
        
        # Rewrite the file
        with open(MATCHES_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['team_a', 'team_b', 'score_a', 'score_b']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for match in matches:
                writer.writerow(match)
