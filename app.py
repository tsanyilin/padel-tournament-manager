import streamlit as st
import pandas as pd
import string
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Padel Master Manager", layout="wide", page_icon="🎾")

# Initialize Session State for data persistence
if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1

# --- Sidebar: Tournament Configuration ---
with st.sidebar:
    st.title("⚙️ Setup")
    mode = st.radio("Tournament Mode", ["Mexicano (Competitive)", "Americano (Social)"])
    
    num_p = st.number_input("Total Players", min_value=4, value=8, step=1)
    num_courts = st.number_input("Number of Courts", min_value=1, value=num_p // 4, step=1)
    
    match_duration = st.slider("Match Duration (Minutes)", 10, 30, 15)
    
    if st.button("🚀 Initialize Tournament", type="primary"):
        st.session_state.players = pd.DataFrame({
            'Player ID': [f"P{i+1}" for i in range(num_p)],
            'Points': [0] * num_p,
            'Matches': [0] * num_p
        })
        st.session_state.round = 1
        st.rerun()

    st.divider()
    st.markdown("### 🙌 Support Development")
    st.write("Created by Lin. Support this tool via PayPay:")
    st.code("PayPay ID: lin_tsanyi")
    st.caption("Your support helps maintain the server and add new features!")

# --- Main Dashboard ---
if st.session_state.players is not None:
    st.title(f"Round {st.session_state.round} | {mode}")
    
    col_play, col_rank = st.columns([2, 1])

    with col_play:
        st.subheader("🎾 Live Court Assignments")
        
        # Court Labeling (A, B, C...)
        court_labels = list(string.ascii_uppercase)[:num_courts]
        
        # Get Rankings (Mexicano Logic: Top players play first)
        sorted_list = st.session_state.players.sort_values(by='Points', ascending=False)['Player ID'].tolist()
        
        max_on_court = num_courts * 4
        on_court = sorted_list[:max_on_court]
        waiting = sorted_list[max_on_court:]
        
        scores_update = {}
        
        # Generate Court Interface
        for i, label in enumerate(court_labels):
            idx = i * 4
            if idx + 3 < len(on_court):
                team1 = [on_court[idx], on_court[idx+1]]
                team2 = [on_court[idx+2], on_court[idx+3]]
                
                with st.expander(f"🏟️ Court {label} - {match_duration} min Match", expanded=True):
                    c_info, c_score = st.columns([2, 1])
                    with c_info:
                        st.markdown(f"**{team1[0]} & {team1[1]}**")
                        st.write("vs")
                        st.markdown(f"**{team2[0]} & {team2[1]}**")
                        st.caption(f"Start Time: {datetime.now().strftime('%H:%M')}")
                    
                    with c_score:
                        s1 = st.number_input(f"T1 Score", min_value=0, key=f"s1_{label}_{st.session_state.round}")
                        s2 = st.number_input(f"T2 Score", min_value=0, key=f"s2_{label}_{st.session_state.round}")
                    
                    # Store scores for the update button
                    for p in team1: scores_update[p] = s1
                    for p in team2: scores_update[p] = s2

        # Waiting / Referee Section
        if waiting:
            st.warning(f"⏳ **Waiting List / Referees (Monitoring Courts):** {', '.join(waiting)}")

        if st.button("✅ Submit All Scores & Next Round", use_container_width=True):
            for p, s in scores_update.items():
                st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Points'] += s
                st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Matches'] += 1
            st.session_state.round += 1
            st.rerun()

    with col_rank:
        st.subheader("🏆 Leaderboard")
        rank_df = st.session_state.players.sort_values(by='Points', ascending=False)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        
        # Visualizing Progress
        st.bar_chart(rank_df.set_index('Player ID')['Points'])

else:
    st.info("👈 Please configure the tournament settings in the sidebar and click 'Initialize Tournament'.")
