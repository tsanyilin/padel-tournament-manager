import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Tournament Setup")
    mode = st.radio("Tournament Mode", ["Mexicano (Competitive)", "Americano (Social)"])
    num_p = st.number_input("Total Players", min_value=4, value=8, step=1)
    
    st.divider()
    st.subheader("🎯 Winning Score")
    score_choice = st.selectbox("Select Target Score", options=[12, 24, 32, "Custom"], index=0)
    target_score = score_choice if score_choice != "Custom" else st.number_input("Enter Custom Score", min_value=1, value=15)
    
    st.divider()
    st.subheader("👥 Player Names")
    player_names_input = []
    input_col1, input_col2 = st.columns(2)
    for i in range(num_p):
        col = input_col1 if i % 2 == 0 else input_col2
        name = col.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"input_p{i}")
        player_names_input.append(name)
    
    st.divider()
    num_courts = st.number_input("Number of Courts", min_value=1, value=max(1, num_p // 4), step=1)
    rental_hours = st.number_input("Total Rental Duration (Hours)", min_value=0.5, value=2.0, step=0.5)
    
    if st.button("🚀 Start & Shuffle", type="primary"):
        shuffled_names = [n.strip() for n in player_names_input if n.strip()]
        if len(shuffled_names) < num_p:
            st.warning("Please fill in all player names!")
        else:
            random.shuffle(shuffled_names)
            st.session_state.players = pd.DataFrame({
                'Player ID': shuffled_names,
                'Points': [0] * len(shuffled_names),
                'Matches': [0] * len(shuffled_names)
            })
            st.session_state.round = 1
            st.session_state.start_time = datetime.now()
            st.rerun()

# --- Main Dashboard ---
if st.session_state.players is not None:
    # --- UPDATED: HH:MM Time Calculation ---
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    time_delta = end_time - datetime.now()
    total_seconds = int(time_delta.total_seconds())
    
    if total_seconds > 0:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        time_display = f"{hours:02d}:{minutes:02d}"
    else:
        time_display = "00:00"

    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("Current Round", st.session_state.round)
    t_col2.metric("Target Score", target_score)
    # Metric shows HH:MM format
    t_col3.metric("Time Remaining", time_display, 
                  delta="- Urgent" if total_seconds < 900 and total_seconds > 0 else None, 
                  delta_color="inverse")

    st.divider()
    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        st.subheader("🎮 Active Matches")
        court_labels = list(string.ascii_uppercase)[:num_courts]
        sorted_list = st.session_state.players.sort_values(by='Points', ascending=False)['Player ID'].tolist()
        
        on_court = sorted_list[:num_courts * 4]
        
        scores_update = {}
        all_courts_finished = True 
        
        for i, label in enumerate(court_labels):
            idx = i * 4
            if idx + 3 < len(on_court):
                p1, p2, p3, p4 = on_court[idx], on_court[idx+1], on_court[idx+2], on_court[idx+3]
                
                s1_key = f"s1_{label}_{st.session_state.round}"
                s2_key = f"s2_{label}_{st.session_state.round}"
                
                if s1_key not in st.session_state: st.session_state[s1_key] = 0
                if s2_key not in st.session_state: st.session_state[s2_key] = 0
                
                s1, s2 = st.session_state[s1_key], st.session_state[s2_key]
                is_finished = s1 >= target_score or s2 >= target_score
                if not is_finished: all_courts_finished = False

                with st.container(border=True):
                    st.markdown(f"### 🏟️ Court {label} {'✅' if is_finished else '🔥'}")
                    
                    total_pts = s1 + s2
                    rotation = [p1, p3, p2, p4] 
                    server_idx = (total_pts // 4) % 4
                    side_idx = total_pts % 2 
                    
                    c1, c2, c3 = st.columns([1, 2, 1])
                    
                    with c1: # TEAM 1
                        st.caption("TEAM 1")
                        st.markdown(f"<div style='border:1px solid black; padding:5px; text-align:center; {'background-color:#c6efce; font-weight:bold;' if server_idx==0 and not is_finished else ''}'>{p1}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='border:1px solid black; padding:5px; text-align:center; {'background-color:#c6efce; font-weight:bold;' if server_idx==2 and not is_finished else ''}'>{p2}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:60px; text-align:center; color:#1f77b4;'>{s1}</div>", unsafe_allow_html=True)
                        if not is_finished:
                            b1_col1, b1_col2 = st.columns(2)
                            if b1_col1.button("＋", key=f"p1_{label}", use_container_width=True):
                                st.session_state[s1_key] = min(target_score, s1 + 1); st.rerun()
                            if b1_col2.button("－", key=f"m1_{label}", use_container_width=True):
                                st.session_state[s1_key] = max(0, s1 - 1); st.rerun()

                    with c2: # Court Visual
                        court_colors = ["white", "white", "white", "white"] 
                        if not is_finished:
                            if server_idx == 0 or server_idx == 2: court_colors[2 if side_idx == 0 else 0] = "#c6efce"
                            else: court_colors[1 if side_idx == 0 else 3] = "#c6efce"

                        court_html = f"""
                        <div style="display: grid; grid-template-columns: 1fr 10px 1fr; grid-template-rows: 80px 80px; border: 2px solid black; background-color: white; margin: 10px auto; width: 85%;">
                            <div style="border: 1px solid #ccc; background-color: {court_colors[0]};"></div>
                            <div style="grid-row: span 2; background-color: #333;"></div>
                            <div style="border: 1px solid #ccc; background-color: {court_colors[1]};"></div>
                            <div style="border: 1px solid #ccc; background-color: {court_colors[2]};"></div>
                            <div style="border: 1px solid #ccc; background-color: {court_colors[3]};"></div>
                        </div>
                        """
                        st.markdown(court_html, unsafe_allow_html=True)
                        if is_finished: st.success(f"WINNER: {p1+' & '+p2 if s1 > s2 else p3+' & '+p4}")

                    with c3: # TEAM 2
                        st.caption("TEAM 2")
                        st.markdown(f"<div style='border:1px solid black; padding:5px; text-align:center; {'background-color:#c6efce; font-weight:bold;' if server_idx==1 and not is_finished else ''}'>{p3}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='border:1px solid black; padding:5px; text-align:center; {'background-color:#c6efce; font-weight:bold;' if server_idx==3 and not is_finished else ''}'>{p4}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:60px; text-align:center; color:#1f77b4;'>{s2}</div>", unsafe_allow_html=True)
                        if not is_finished:
                            b2_col1, b2_col2 = st.columns(2)
                            if b2_col1.button("＋", key=f"p2_{label}", use_container_width=True):
                                st.session_state[s2_key] = min(target_score, s2 + 1); st.rerun()
                            if b2_col2.button("－", key=f"m2_{label}", use_container_width=True):
                                st.session_state[s2_key] = max(0, s2 - 1); st.rerun()

                    scores_update[p1] = s1; scores_update[p2] = s1
                    scores_update[p3] = s2; scores_update[p4] = s2

        if all_courts_finished:
            if st.button("🎉 Confirm & End Round", type="primary", use_container_width=True):
                for p, s in scores_update.items():
                    st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Points'] += s
                    st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Matches'] += 1
                st.session_state.round += 1
                st.rerun()

    with col_rank:
        st.subheader("🏆 Leaderboard")
        rank_df = st.session_state.players.sort_values(by='Points', ascending=False)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Setup your tournament in the sidebar to begin!")
