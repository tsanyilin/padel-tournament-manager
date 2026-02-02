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
                'Points': [0] * num_p,
                'Matches': [0] * num_p
            })
            st.session_state.round = 1
            st.session_state.start_time = datetime.now()
            st.rerun()

    if st.button("🔄 Reset Tournament"):
        st.session_state.players = None
        st.rerun()

# --- Main Dashboard ---
if st.session_state.players is not None:
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    time_left = end_time - datetime.now()
    minutes_left = max(0, int(time_left.total_seconds() / 60))

    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("Current Round", st.session_state.round)
    t_col2.metric("Target Score", target_score)
    t_col3.metric("Time Remaining", f"{minutes_left} min", 
                  delta="- Urgent" if minutes_left < 15 else None, delta_color="inverse")

    st.divider()
    col_play, col_rank = st.columns([2, 1])

    with col_play:
        st.subheader("🎮 Active Matches")
        court_labels = list(string.ascii_uppercase)[:num_courts]
        sorted_list = st.session_state.players.sort_values(by='Points', ascending=False)['Player ID'].tolist()
        
        on_court = sorted_list[:num_courts * 4]
        waiting = sorted_list[num_courts * 4:]
        
        scores_update = {}
        all_courts_finished = True 
        
        for i, label in enumerate(court_labels):
            idx = i * 4
            if idx + 3 < len(on_court):
                # Teams: T1(P1, P2) vs T2(P3, P4)
                p1, p2, p3, p4 = on_court[idx], on_court[idx+1], on_court[idx+2], on_court[idx+3]
                
                s1_key = f"s1_{label}_{st.session_state.round}"
                s2_key = f"s2_{label}_{st.session_state.round}"
                current_s1 = st.session_state.get(s1_key, 0)
                current_s2 = st.session_state.get(s2_key, 0)
                is_finished = current_s1 >= target_score or current_s2 >= target_score

                with st.expander(f"🏟️ Court {label} {'✅ FINISHED' if is_finished else '🔥 LIVE'}", expanded=not is_finished):
                    c_info, c_score = st.columns([2, 1])
                    
                    with c_score:
                        s1 = st.number_input(f"T1 Score", min_value=0, max_value=target_score, key=s1_key, disabled=is_finished)
                        s2 = st.number_input(f"T2 Score", min_value=0, max_value=target_score, key=s2_key, disabled=is_finished)
                        if not is_finished: all_courts_finished = False

                    with c_info:
                        st.markdown(f"**{p1} & {p2}** vs **{p3} & {p4}**")
                        
                        if not is_finished:
                            total_pts = s1 + s2
                            # Server Rotation Logic (Changes every 4 points)
                            # 0-3: P1, 4-7: P3, 8-11: P2, 12-15: P4...
                            rotation = [p1, p3, p2, p4]
                            server_idx = (total_pts // 4) % 4
                            current_server = rotation[server_idx]
                            
                            # Side Logic (Every point)
                            side = "RIGHT (Deuce)" if total_pts % 2 == 0 else "LEFT (Ad)"
                            
                            st.info(f"👤 **Server:** {current_server}")
                            st.write(f"🎾 **Side:** {side}")
                        else:
                            st.success(f"Winner: {p1+' & '+p2 if s1 > s2 else p3+' & '+p4}")
                    
                    for p in [p1, p2]: scores_update[p] = s1
                    for p in [p3, p4]: scores_update[p] = s2

        if waiting:
            st.warning(f"⏳ **Waiting List:** {', '.join(waiting)}")

        if all_courts_finished:
            if st.button("🎉 End Round & Rotate", type="primary", use_container_width=True):
                for p, s in scores_update.items():
                    st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Points'] += s
                    st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Matches'] += 1
                st.session_state.round += 1
                st.rerun()
        else:
            st.button(f"Waiting for matches to hit {target_score}...", disabled=True, use_container_width=True)

    with col_rank:
        st.subheader("🏆 Leaderboard")
        rank_df = st.session_state.players.sort_values(by='Points', ascending=False)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        st.bar_chart(rank_df.set_index('Player ID')['Points'])
