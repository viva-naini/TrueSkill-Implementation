"""
Match entry page with admin functionality for recording games and undoing matches.
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import logic
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logic import (
    load_players, save_players, load_matches, save_match,
    record_game, recalculate_all_ratings, delete_last_match,
    add_player, PLAYERS_FILE
)
from ui import apply_theme_and_branding


st.set_page_config(page_title="Match Entry", layout="wide")
apply_theme_and_branding()
st.markdown('<div class="usr-brand">', unsafe_allow_html=True)
st.title("⚔️ Match Entry")
st.markdown("---")

# Load current players
players = load_players()

# Section: Add New Players
st.subheader("➕ Add New Players")
with st.form("add_player_form"):
    new_player_name = st.text_input("Player Name", placeholder="Enter player name...")
    add_player_button = st.form_submit_button("Add Player", type="primary")
    
    if add_player_button:
        if new_player_name and new_player_name.strip():
            name = new_player_name.strip()
            if name in players:
                st.warning(f"Player '{name}' already exists!")
            else:
                players = add_player(name, players)
                st.success(f"Player '{name}' added successfully!")
                st.rerun()
        else:
            st.error("Please enter a player name.")

st.markdown("---")

# Section: Record Match
st.subheader("📝 Record New Match")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Team A")
    st.caption("Select **2–7** players.")
    # Get Team B selections to filter options
    team_b_selected = st.session_state.get("team_b_players_input", [])
    # Filter out players already selected in Team B
    team_a_options = [p for p in sorted(players.keys()) if p not in team_b_selected]
    team_a = st.multiselect(
        "Select Players",
        options=team_a_options if players else [],
        max_selections=7,
        key="team_a_players_input"
    )
    score_a = st.number_input(
        "Team A Score",
        min_value=0,
        value=0,
        key="score_a_input"
    )

with col2:
    st.markdown("### Team B")
    st.caption("Select **2–7** players.")
    # Get Team A selections to filter options
    team_a_selected = st.session_state.get("team_a_players_input", [])
    # Filter out players already selected in Team A
    team_b_options = [p for p in sorted(players.keys()) if p not in team_a_selected]
    team_b = st.multiselect(
        "Select Players",
        options=team_b_options if players else [],
        max_selections=7,
        key="team_b_players_input"
    )
    score_b = st.number_input(
        "Team B Score",
        min_value=0,
        value=0,
        key="score_b_input"
    )

submit_match = st.button("Record Match", type="primary", use_container_width=True)

if submit_match:
        # Validation
        errors = []
        
        if len(team_a) < 2 or len(team_a) > 7:
            errors.append("Team A must have between 2 and 7 players.")
        if len(team_b) < 2 or len(team_b) > 7:
            errors.append("Team B must have between 2 and 7 players.")
        
        # Check for overlapping players
        overlap = set(team_a) & set(team_b)
        if overlap:
            errors.append(f"Players cannot be on both teams: {', '.join(overlap)}")
        
        # Check for zero scores
        if score_a == 0 and score_b == 0:
            errors.append("At least one team must score points.")
        
        # Check if both teams have equal size (optional, but common in Ultimate)
        if len(team_a) != len(team_b):
            st.info("ℹ️ Teams have different sizes. This is allowed but uncommon in Ultimate.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Record the match
            try:
                players = record_game(team_a, team_b, score_a, score_b, players)
                save_players(players)
                save_match(team_a, team_b, score_a, score_b)
                
                winner = "Team A" if score_a > score_b else "Team B"
                st.success(f"✅ Match recorded! {winner} wins {max(score_a, score_b)}-{min(score_a, score_b)}")
                # Clear form state after successful submission
                st.session_state["team_a_players_input"] = []
                st.session_state["team_b_players_input"] = []
                st.session_state["score_a_input"] = 0
                st.session_state["score_b_input"] = 0
                st.rerun()
            except Exception as e:
                st.error(f"Error recording match: {str(e)}")

st.markdown("---")

# Section: Match History
st.subheader("📜 Match History")

matches = load_matches()

if not matches:
    st.info("No matches recorded yet.")
else:
    # Display last 10 matches
    recent_matches = matches[-10:][::-1]  # Show most recent first
    
    match_data = []
    for i, match in enumerate(recent_matches):
        team_a = match['team_a'].split(',')
        team_b = match['team_b'].split(',')
        score_a = int(match['score_a'])
        score_b = int(match['score_b'])
        
        match_data.append({
            'Game #': len(matches) - i,
            'Team A': ', '.join(team_a),
            'Score A': score_a,
            'Score B': score_b,
            'Team B': ', '.join(team_b),
            'Winner': 'Team A' if score_a > score_b else 'Team B' if score_b > score_a else 'Tie'
        })
    
    df_matches = pd.DataFrame(match_data)
    st.dataframe(df_matches, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Undo Last Game button
    st.subheader("🔄 Undo Last Game")
    st.warning("⚠️ Undoing will delete the last match and recalculate all ratings from scratch.")
    
    if st.button("Undo Last Game", type="secondary"):
        if matches:
            try:
                delete_last_match()
                recalculate_all_ratings()
                st.success("✅ Last game undone! All ratings have been recalculated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error undoing match: {str(e)}")
        else:
            st.error("No matches to undo.")

st.markdown("</div>", unsafe_allow_html=True)
