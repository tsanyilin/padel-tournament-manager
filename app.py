import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

# Initialize Session State
if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Sidebar: Tournament Configuration ---
with st.sidebar:
    st.title("⚙️ Tournament Setup")
    mode = st.radio("Tournament Mode", ["Mexicano (Competitive)", "Americano (Social)"])
    
    # 1. Select total number of players
    num_p = st.number_input("Total Players", min_value=4, value=8, step=1)
    
    st.divider()
    
    # 2. Dynamic Input Fields for Player Names
    st.subheader("👥 Player Names")
    player_names_input = []
    
    # Two-column layout for player name inputs
    input_col1, input_col2 = st.columns(2)
    for i in range(num_p):
        col = input_col1 if i % 2 == 0 else input_col2
        name = col.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"input_p{i}")
        player_names_input.append(name)
    
    st.divider()
    
    num_courts = st.number_input("Number of Courts", min_value=1, value=max(1, num_p // 4), step=1)
    rental_hours = st.number_input("Total Rental Duration (Hours)", min_value=0.5, value=2.0, step=0.5)
    
    if st.button("🚀 Start & Shuffle", type="primary"):
        # 3. Validation and Random Shuffling
        shuffled_names = [n.strip() for n in player_names_input if n.strip()]
        if len(shuffled_names) < num_p:
            st.warning("Please fill in all player names before starting!")
        else:
            random.shuffle(shuffled_names) # Execute random shuffle
            
            st.session_state.players = pd.DataFrame({
                'Player ID': shuffled_names,
                'Points': [0] * num_p,
                'Matches': [0] * num_p
            })
            st.session_state.round = 1
            st.session_state.start_time = datetime.now()
            st.rerun()

    st.divider()
    st.markdown("### 🙌 Support Development")
    st.write("Created by Lin. Support via PayPay:")
    st.code("PayPay ID: tsanyilin")

# --- Main Dashboard ---
if st.session_state.players is not None:
    # Calculate Time Management
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    time_left = end_time - datetime.now()
    minutes_left = max(0, int(time_left.total_seconds() / 60))

    # Top Status Bar
    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("Current Round", st.session_state.round)
    t_col2.metric("Total Rental Time", f"{rental_hours}h")
    # Metric turns red (Inverse) if less than 15 minutes left
    t_col3.metric("Rental Time Left", f"{minutes_left} min", 
                  delta="- Urgent" if minutes_left < 15 else None, 
                  delta_color="inverse")

    st.divider()
    
    col_play, col_rank = st.columns([2, 1])

    with col_play:
        st.subheader("🎮 Active Matches")
        court_labels = list(string.ascii_uppercase)[:num_courts]
        
        # Sorting for Mexicano Logic: Based on points
        sorted_list = st.session_state.players.sort_values(by='Points', ascending=False)['Player ID'].tolist()
        
        max_on_court = num_courts * 4
        on_court = sorted_list[:max_on_court]
        waiting = sorted_list[max_on_court:]
        
        scores_update = {}
        
        for i, label in enumerate(court_labels):
            idx = i * 4
            if idx + 3 < len(on_court):
                t1, t2 = [on_court[idx], on_court[idx+1]], [on_court[idx+2], on_court[idx+3]]
                
                with st.expander(f"🏟️ Court {label} - [Round {st.session_state.round}]", expanded=True):
                    c_info, c_score = st.columns([2, 1])
                    with c_info:
                        st.markdown(f"**{t1[0]} & {t1[1]}** vs **{t2[0]} & {t2[1]}**")
                        st.caption(f"Rental Ends at: {end_time.strftime('%H:%M')}")
                    
                    with c_score:
                        s1 = st.number_input(f"T1 Score", min_value=0, key=f"s1_{label}_{st.session_state.round}")
                        s2 = st.number_input(f"T2 Score", min_value=0, key=f"s2_{label}_{st.session_state.round}")
                    
                    for p in t1: scores_update[p] = s1
                    for p in t2: scores_update[p] = s2

        if waiting:
            st.warning(f"⏳ **Waiting List / Next Up:** {', '.join(waiting)}")

        if st.button("✅ Submit & Next Round", use_container_width=True):
            for p, s in scores_update.items():
                st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Points'] += s
                st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Matches'] += 1
            st.session_state.round += 1
            st.rerun()

    with col_rank:
        st.subheader("🏆 Leaderboard")
        rank_df = st.session_state.players.sort_values(by='Points', ascending=False)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        st.bar_chart(rank_df.set_index('Player ID')['Points'])

else:
    st.info("👈 Please enter player names in the sidebar and click 'Start & Shuffle' to begin.")
