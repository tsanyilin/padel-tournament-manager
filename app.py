import streamlit as st
import pandas as pd
import string
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

# 1. 預定義 8 人 Americano 輪轉表 (P1-P8)
# 格式: Round#: [ [Court A Team 1, Team 2], [Court B Team 1, Team 2] ]
AMERICANO_8_SCHEDULE = {
    1: [[["P1", "P2"], ["P3", "P4"]], [["P5", "P6"], ["P7", "P8"]]],
    2: [[["P1", "P3"], ["P5", "P7"]], [["P2", "P4"], ["P6", "P8"]]],
    3: [[["P1", "P4"], ["P2", "P6"]], [["P3", "P5"], ["P8", "P7"]]],
    4: [[["P1", "P5"], ["P4", "P8"]], [["P2", "P3"], ["P6", "P7"]]],
    5: [[["P1", "P6"], ["P8", "P3"]], [["P5", "P4"], ["P7", "P2"]]],
    6: [[["P1", "P7"], ["P6", "P5"]], [["P8", "P2"], ["P4", "P3"]]],
    7: [[["P1", "P8"], ["P7", "P4"]], [["P6", "P3"], ["P5", "P2"]]]
}

if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Tournament Setup")
    mode = st.radio("Mode", ["Americano (Social)", "Mexicano (Competitive)"])
    num_p = st.number_input("Total Players", min_value=8, max_value=8, value=8) # 暫定固定8人
    rental_hours = st.number_input("Rental Duration (Hours)", min_value=0.5, value=2.0, step=0.5)
    
    if st.button("🚀 Start Tournament", type="primary"):
        st.session_state.players = pd.DataFrame({
            'Player ID': [f"P{i+1}" for i in range(num_p)],
            'Points': [0] * num_p
        })
        st.session_state.round = 1
        st.session_state.start_time = datetime.now()
        st.rerun()

# --- Main Dashboard ---
if st.session_state.players is not None:
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    
    col_play, col_rank = st.columns([2, 1])

    with col_play:
        st.subheader(f"🔥 Round {st.session_state.round} - Active Matches")
        court_labels = ["A", "B"]
        
        # 取得當前輪次對戰
        current_round_data = AMERICANO_8_SCHEDULE.get(st.session_state.round, [])
        scores_update = {}

        for i, label in enumerate(court_labels):
            match = current_round_data[i]
            t1, t2 = match[0], match[1]
            
            with st.expander(f"🏟️ Court {label}", expanded=True):
                c_info, c_score = st.columns([2, 1])
                with c_info:
                    st.markdown(f"**{t1[0]} & {t1[1]}** vs **{t2[0]} & {t2[1]}**")
                with c_score:
                    s1 = st.number_input(f"T1 Score", min_value=0, key=f"s1_{label}_{st.session_state.round}")
                    s2 = st.number_input(f"T2 Score", min_value=0, key=f"s2_{label}_{st.session_state.round}")
                for p in t1: scores_update[p] = s1
                for p in t2: scores_update[p] = s2

        # --- 重要：下一輪預告 ---
        next_round = st.session_state.round + 1
        if next_round in AMERICANO_8_SCHEDULE:
            st.divider()
            st.subheader("⏭️ Next Round Preview (Get Ready!)")
            next_data = AMERICANO_8_SCHEDULE[next_round]
            n_col1, n_col2 = st.columns(2)
            with n_col1:
                st.write(f"**Court A:** {next_data[0][0][0]}&{next_data[0][0][1]} vs {next_data[0][1][0]}&{next_data[0][1][1]}")
            with n_col2:
                st.write(f"**Court B:** {next_data[1][0][0]}&{next_data[1][0][1]} vs {next_data[1][1][0]}&{next_data[1][1][1]}")

        if st.button("✅ Submit & Next Round", use_container_width=True):
            for p, s in scores_update.items():
                st.session_state.players.loc[st.session_state.players['Player ID'] == p, 'Points'] += s
            st.session_state.round += 1
            st.rerun()

    with col_rank:
        st.subheader("🏆 Leaderboard")
        st.dataframe(st.session_state.players.sort_values(by='Points', ascending=False), use_container_width=True, hide_index=True)
