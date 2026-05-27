1. Executive Summary
A standalone web application to track and rank Ultimate Frisbee players in a local community. The system uses the OpenSkill algorithm (a Bayesian rating system) to determine individual skill based on team-based match results, specifically accounting for the Margin of Victory (MoV).
2. Technical Stack
Framework: Streamlit (Python)
Engine: openskill.py (Plackett-Luce Model)
Storage: Local CSV (players.csv, matches.csv)
Navigation: Streamlit Multi-page (st.navigation)
3. Data Architecture & Logic
A. The Ranking Algorithm
Base: Every player starts at $\mu = 25$ and $\sigma = 8.33$.
Sorting Metric (Conservative Rating): $R = \mu - 3\sigma$.
Margin of Victory (MoV): A logarithmic multiplier applied to the $\Delta\mu$ (change in Mu).
$Multiplier = 1 + (\ln(Margin + 1) / \ln(15))$
This ensures a 15-0 win moves the needle more than a 15-14 win.
B. Persistence & "Undo" Strategy
Persistence: All match results are appended to matches.csv. Player states are saved in players.csv.
The Rebuild Logic: Because Bayesian updates are order-dependent, the "Undo" function will:
Delete the last row from matches.csv.
Reset all player ratings in the session.
Re-process every match in the CSV from the beginning to ensure mathematical consistency.
4. UI/UX Requirements
Page 1: Leaderboard (Public)
Visual Reference: llm-stats.com
Components:
Searchable data table.
Rank column based on Conservative Rating.
Sigma column rendered as a progress bar (0 to 8.33).
Record column showing "Wins - Losses".
Page 2: Match Entry (Admin)
Team Selection: Multi-select widgets for Team A and Team B (supports 2v2 to 7v7).
Score Input: Integer inputs for both teams.
Validation: Prevent overlapping players; prevent zero-score entries.
History: A table showing the last 10 games with an "Undo Last Game" button.

