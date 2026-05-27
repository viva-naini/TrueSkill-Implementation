"""
Leaderboard page displaying player rankings with styled data table.
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import logic
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logic import load_players, get_player_records, mu_to_usr, sigma_to_usr_sigma, conservative_usr, DEFAULT_SIGMA
from ui import apply_theme_and_branding


st.set_page_config(page_title="Leaderboard", layout="wide")
apply_theme_and_branding()
st.markdown('<div class="usr-brand">', unsafe_allow_html=True)
st.title("🏆 Leaderboard")
st.markdown("---")

# Load data
players = load_players()

if not players:
    st.info("No players found. Add players through the Match Entry page.")
else:
    # Get player records
    records = get_player_records(players)
    
    # Prepare data for DataFrame
    data = []
    for name, rating in players.items():
        wins, losses = records.get(name, (0, 0))
        conservative_rating = conservative_usr(rating.mu, rating.sigma)
        skill_rating = mu_to_usr(rating.mu)
        uncertainty = sigma_to_usr_sigma(rating.sigma)
        data.append({
            'Player': name,
            'USR': conservative_rating,
            'Mu': skill_rating,
            'Sigma': uncertainty,
            'Wins': wins,
            'Losses': losses,
            'Record': f"{wins}-{losses}"
        })
    
    # Create DataFrame and sort by conservative rating (descending)
    df = pd.DataFrame(data)
    df = df.sort_values('USR', ascending=False).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)
    
    # Reorder columns
    df = df[['Rank', 'Player', 'USR', 'Mu', 'Sigma', 'Record', 'Wins', 'Losses']]
    
    # Configure column display
    column_config = {
        'Rank': st.column_config.NumberColumn(
            'Rank',
            help='Rank based on Conservative USR rating',
            width='small'
        ),
        'Player': st.column_config.TextColumn(
            'Player',
            help='Player name',
            width='medium'
        ),
        'USR': st.column_config.NumberColumn(
            'Skill Rating',
            help='Conservative skill rating (centered at 1000). Used for rankings.',
            format='%.0f',
            width='small'
        ),
        'Mu': st.column_config.NumberColumn(
            'Skill',
            help='Mean skill rating on USR scale (centered at 1000)',
            format='%.0f',
            width='small'
        ),
        'Sigma': st.column_config.ProgressColumn(
            'Uncertainty',
            help='Uncertainty in skill rating (lower is better)',
            min_value=0.0,
            max_value=DEFAULT_SIGMA * 40.0,
            format='%.0f',
            width='medium'
        ),
        'Record': st.column_config.TextColumn(
            'Record',
            help='Wins - Losses',
            width='small'
        ),
        'Wins': st.column_config.NumberColumn(
            'Wins',
            help='Total wins',
            width='small'
        ),
        'Losses': st.column_config.NumberColumn(
            'Losses',
            help='Total losses',
            width='small'
        )
    }
    
    # Display searchable data table
    search_term = st.text_input("🔍 Search players", placeholder="Type to filter...")
    
    if search_term:
        df_filtered = df[df['Player'].str.contains(search_term, case=False, na=False)]
    else:
        df_filtered = df
    
    # Hide the Wins and Losses columns from display but keep them for sorting/filtering
    display_df = df_filtered[['Rank', 'Player', 'USR', 'Mu', 'Sigma', 'Record']]
    
    st.dataframe(
        display_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )
    
    # Display summary stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(players))
    with col2:
        st.metric("Total Games", sum(w + l for w, l in records.values()) // 2 if records else 0)
    with col3:
        if records:
            total_wins = sum(w for w, l in records.values())
            st.metric("Total Games Played", total_wins + sum(l for w, l in records.values()))
    with col4:
        if df_filtered is not None and len(df_filtered) > 0:
            st.metric("Top Skill Rating", f"{df_filtered.iloc[0]['USR']:.0f}")

st.markdown("</div>", unsafe_allow_html=True)
