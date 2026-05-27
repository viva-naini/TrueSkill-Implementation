"""
Player page: per-player match history and stats.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import logic/ui
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from logic import (
    load_players,
    get_player_records,
    get_player_match_history,
    mu_to_usr,
    sigma_to_usr_sigma,
    conservative_usr,
)
from ui import apply_theme_and_branding


st.set_page_config(page_title="Player", layout="wide")
apply_theme_and_branding()
st.markdown('<div class="usr-brand">', unsafe_allow_html=True)

st.title("👤 Player")
st.markdown("---")

players = load_players()
if not players:
    st.info("No players found yet. Add players on the Match Entry page.")
    st.stop()

player_name = st.selectbox("Select a player", options=sorted(players.keys()))
rating = players[player_name]
records = get_player_records(players)
wins, losses = records.get(player_name, (0, 0))

# Convert to USR scale (centered at 1000)
skill_rating = mu_to_usr(rating.mu)
conservative_skill_rating = conservative_usr(rating.mu, rating.sigma)
uncertainty = sigma_to_usr_sigma(rating.sigma)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 5px; margin-bottom: 0.5rem;">'
        '<span><strong>Skill Rating</strong></span>'
        '<div class="usr-tooltip">'
        '<span style="font-size: 0.9em;">ℹ️</span>'
        '<span class="usr-tooltiptext">Player\'s skill rating on the USR scale (centered at 1000). Higher values indicate greater skill.</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.metric("Skill Rating", f"{skill_rating:.0f}", label_visibility="collapsed")
with col2:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 5px; margin-bottom: 0.5rem;">'
        '<span><strong>Conservative Skill Rating</strong></span>'
        '<div class="usr-tooltip">'
        '<span style="font-size: 0.9em;">ℹ️</span>'
        '<span class="usr-tooltiptext">Conservative skill rating (Skill Rating - 3×Uncertainty). Used for rankings to account for rating uncertainty. Lower uncertainty leads to higher conservative rating.</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.metric("Conservative Skill Rating", f"{conservative_skill_rating:.0f}", label_visibility="collapsed")
with col3:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 5px; margin-bottom: 0.5rem;">'
        '<span><strong>Uncertainty</strong></span>'
        '<div class="usr-tooltip">'
        '<span style="font-size: 0.9em;">ℹ️</span>'
        '<span class="usr-tooltiptext">Uncertainty in the skill rating (lower is better). Decreases as more games are played. New players start with higher uncertainty.</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.metric("Uncertainty", f"{uncertainty:.0f}", label_visibility="collapsed")
with col4:
    st.metric("Record", f"{wins}-{losses}")

history = get_player_match_history(player_name)
if not history:
    st.info("No match history for this player yet.")
    st.stop()

df = pd.DataFrame(history)

# Quick stats from history
df["Is Win"] = df["Result"] == "W"
df["Is Loss"] = df["Result"] == "L"
df["Point Diff"] = df["Score For"] - df["Score Against"]

st.markdown("### Stats")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Games Played", len(df))
with col2:
    st.metric("Win %", f"{(df['Is Win'].mean() * 100):.1f}%")
with col3:
    st.metric("Avg Point Diff", f"{df['Point Diff'].mean():+.2f}")
with col4:
    st.metric("Avg Margin", f"{df['Margin'].mean():.2f}")

st.markdown("### Match History")
st.dataframe(
    df[["Game #", "Result", "Score For", "Score Against", "Margin", "Teammates", "Opponents"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Game #": st.column_config.NumberColumn("Game #", width="small"),
        "Result": st.column_config.TextColumn("Result", width="small"),
        "Score For": st.column_config.NumberColumn("For", width="small"),
        "Score Against": st.column_config.NumberColumn("Against", width="small"),
        "Margin": st.column_config.NumberColumn("MoV", width="small"),
        "Teammates": st.column_config.TextColumn("Teammates", width="large"),
        "Opponents": st.column_config.TextColumn("Opponents", width="large"),
    },
)

st.markdown("</div>", unsafe_allow_html=True)

