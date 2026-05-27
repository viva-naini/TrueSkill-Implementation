"""
Ultimate Frisbee Power Rankings - Main Application Entry Point
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Ultimate Skill Rating (USR) Leaderboard",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main landing page content
from ui import apply_theme_and_branding

apply_theme_and_branding()
st.markdown('<div class="usr-brand">', unsafe_allow_html=True)
st.title("🥏 Ultimate Skill Rating (USR) Leaderboard 🥏")
st.markdown("---")

st.markdown("""
Welcome to **USR (Ultimate Skill Rating)**.

This application uses the **OpenSkill** (Plackett-Luce) algorithm with **Margin of Victory** adjustments
to calculate player skill ratings based on team match results.

### Key Features:
- 🏆 **Leaderboard**: View player rankings sorted by Conservative Skill Rating (centered at 1000)
- ⚔️ **Match Entry**: Record matches and manage player data
- 📊 **Dynamic Skill Ratings**: Skill ratings adjust based on win/loss and margin of victory

### How It Works:
1. **Skill Rating Scale**: All skill ratings are displayed on the USR scale, centered at **1000**. New players start near 1000, and ratings move above or below based on wins and losses.
2. **Conservative Skill Rating**: Used for rankings = Skill Rating - 3×Uncertainty (accounts for rating uncertainty)
3. **Margin of Victory**: Larger wins (e.g., 15-0) have more impact on skill rating changes than close games (15-14)
4. **Team-Based**: Skill ratings are calculated from team match results using the OpenSkill algorithm

### Navigation:
Use the sidebar to navigate to:
- **🏆 Leaderboard**: View current player rankings
- **⚔️ Match Entry**: Record new matches and manage players

---
""")

# Footer
st.sidebar.markdown("### About")
st.sidebar.info(
    """
    **USR — Ultimate Skill Rating**
    
    Uses the OpenSkill (Plackett-Luce) algorithm with Margin of Victory adjustments.
    
    Skill ratings are displayed on a scale centered at 1000.
    Rankings use Conservative Skill Rating: Skill Rating - 3×Uncertainty
    """
)

st.markdown("</div>", unsafe_allow_html=True)
