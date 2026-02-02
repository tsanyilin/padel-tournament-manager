import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

# --- Custom CSS for Point Selection Buttons ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em; font-weight: bold; }
    .main-header { font-size: 24px; font-weight: bold; color: #1f77b4; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Sidebar: Tournament Setup ---
with st.sidebar:
    st.title("🎾 My Tournament")
    
    st.subheader("Tournament Format")
    mode = st.radio("Format", ["Americano", "Mexicano"], horizontal=True, label_visibility="collapsed")
    
    st.subheader("Number of Players")
    num_p = st.number_input("Players", min_value=4, value=8, step=1, label_visibility="collapsed")
    
    st.divider()
    
    st.subheader("Point System (Target Score)")
    # Emulating the grid button selection from your reference
    score_cols = st.columns(3)
    preset_scores = [12, 16, 21, 24, 32, "Custom"]
    
    if 'target_score' not in st.session_state:
        st.session_state.target_score = 12

    for idx, score in enumerate(preset_scores):
        col = score_cols[idx % 3]
        if col.button(str(score), key=f"btn_{score}", use_container_width=True):
            st.session_state.target_score = score

    if st.session_state.target_score == "Custom":
        final_target = st.number_input("Enter Score", min_value=1, value=15)
    else:
        final_target = st.session_state.target_score
    
    st.info(f"Target: {final_target} points")

    st.divider()
    
    st.subheader("Player Names")
    player_names_input = []
    p_cols = st.columns(2)
    for i in range(num_p):
        col = p_cols[i % 2]
        name = col.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"input_p{i}", label_visibility="collapsed")
        player_names_input.append(name)
    
    st.divider()
    
    num_courts = st.number_input("Number of Courts", min_value=1, value=max(1, num_p // 4), step=1)
    rental_hours = st.number_input("Rental Duration (Hours)", min_value=0.5, value=2.0, step=0.5)
    
    if st.button("🚀 GENERATE MATCHES", type="primary", use_container_width=True):
        shuffled_names = [n.strip() for n in player_names_input if n.strip()]
        if len(shuffled_names) < num_p:
            st.warning("Please fill all names!")
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
    # --- HH:MM Time Remaining ---
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    time_delta = end_time - datetime.now()
    total_sec = max(0, int(time_delta.total_seconds()))
    time_display = f"{total_sec // 3600:02d}:{(total_sec % 3600) // 60:02d}"

    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("Round", st.session_state.round)
    t_col2.metric("Target", f"{final_target} pts")
    t_col3.metric("Time Left", time_display, delta="- Urgent" if 0 < total_sec < 900 else None, delta_color="inverse")

    st.divider()
    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        st.subheader("🎮 Active Matches")
        court_labels = list(string.ascii_uppercase)[:num_courts]
        sorted_list = st.session_state.players.sort_values(by='Points', ascending=False)['Player ID'].tolist()
        on_court = sorted_list[:num_courts * 4]
        
        scores_update = {}
        all_finished = True 
        
        for i, label in enumerate(court_labels):
            idx = i * 4
            if idx + 3 < len(on_court):
                p1, p2, p3, p4 = on_court[idx], on_court[idx+1], on_court[idx+2], on_court[idx+3]
                s1_k, s2_k = f"s1_{label}_{st.session_state.round}", f"s2_{label}_{st.session_state.round}"
                
                if s1_k not in st.session_state: st.session_state[s1_k] = 0
                if s2_k not in st.session_state: st.session_state[s2_k] = 0
                
                s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
                finished = s1 >= final_target or s2 >= final_target
                if not finished: all_finished = False

                with st.container(border=True):
                    st.markdown(f"**COURT {label}** <span style='float:right;'>{'✅' if finished else '🎾'}</span>", unsafe_allow_html=True)
                    
                    # Logic for Service and Server Visualization
                    total = s1 + s2
                    rotation = [p1, p3, p2, p4] 
                    srv_idx = (total // 4) % 4
                    side_idx = total % 2 
                    
                    c1, c2, c3 = st.columns([1, 1.5, 1])
                    
                    with c1: # Team 1
                        for j, p in enumerate([p1, p2]):
                            is_srv = (srv_idx == (0 if j==0 else 2)) and not finished
                            st.markdown(f"<div style='border:1px solid #ddd; padding:8px; text-align:center; background-color:{'#c6efce' if is_srv else 'white'}; font-weight:{'bold' if is_srv else 'normal'};'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:64px; font-weight:bold; text-align:center; color:#1f77b4;'>{s1}</div>", unsafe_allow_html=True)
                        if not finished:
                            b_c = st.columns(2)
                            if b_c[0].button("＋", key=f"p1_{label}"): st.session_state[s1_k] = min(final_target, s1+1); st.rerun()
                            if b_c[1].button("－", key=f"m1_{label}"): st.session_state[s1_k] = max(0, s1-1); st.rerun()

                    with c2: # Court Diagram
                        colors = ["#f8f9fa"] * 4
                        if not finished:
                            if srv_idx in [0, 2]: colors[2 if side_idx == 0 else 0] = "#c6efce"
                            else: colors[1 if side_idx == 0 else 3] = "#c6efce"
                        
                        st.markdown(f"""
                        <div style="display: grid; grid-template-columns: 1fr 10px 1fr; grid-template-rows: 80px 80px; border: 2px solid black; background-color: white; margin: 10px auto; width: 90%;">
                            <div style="background-color:{colors[0]}; border:1px solid #eee;"></div>
                            <div style="grid-row:span 2; background-color:#333;"></div>
                            <div style="background-color:{colors[1]}; border:1px solid #eee;"></div>
                            <div style="background-color:{colors[2]}; border:1px solid #eee;"></div>
                            <div style="background-color:{colors[3]}; border:1px solid #eee;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        if finished: st.success("Match Over")

                    with c3: # Team 2
                        for j, p in enumerate([p3, p4]):
                            is_srv = (srv_idx == (1 if j==0 else 3)) and not finished
                            st.markdown(f"<div style='border:1px solid #ddd; padding:8px; text-align:center; background-color:{'#c6efce' if is_srv else 'white'}; font-weight:{'bold' if is_srv else 'normal'};'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:64px; font-weight:bold; text-align:center; color:#1f77b4;'>{s2}</div>", unsafe_allow_html=True)
                        if not finished:
                            b_c = st.columns(2)
                            if b_c[0].button("＋", key=f"p2_{label}"): st.session_state[s2_k] = min(final_target, s2+1); st.rerun()
                            if b_c[1].button("－", key=f"m2_{label}"): st.session_state[s2_k] = max(0, s2-1); st.rerun()

                    scores_update[p1] = s1; scores_update[p2] = s1
                    scores_update[p3] = s2; scores_update[p4] = s2

        if all_finished:
            if st.button("🎉 FINISH ROUND & ROTATE", type="primary", use_container_width=True):
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
    st.info("👈 Set your tournament parameters and click 'GENERATE MATCHES' to begin!")
