import streamlit as st
import pandas as pd
import string
import random
import time

# --- 1. Translation Dictionary ---
LANG_DICT = {
    "English": {
        "setup": "Tournament Setup",
        "format": "Tournament Format",
        "logic_play": "Points to Play (Total)",
        "logic_win": "Points to Win",
        "logic_time": "Time Play",
        "duration": "Duration (Minutes)",
        "target": "Target Score",
        "courts": "Number of Courts",
        "generate": "🚀 GENERATE",
        "confirm": "🎉 CONFIRM & NEXT",
        "finished": "FINISHED",
        "live": "LIVE",
        "team": "TEAM",
        "leaderboard": "Leaderboard",
        "next_up": "👀 NEXT UP",
        "time_up": "⏰ TIME IS UP!"
    },
    "日本語": {
        "setup": "大会設定",
        "format": "試合形式",
        "logic_play": "総得點制",
        "logic_win": "勝利點制",
        "logic_time": "時間制",
        "duration": "試合時間 (分)",
        "target": "目標スコア",
        "courts": "コート數",
        "generate": "🚀 試合開始",
        "confirm": "🎉 確定して次へ",
        "finished": "終了",
        "live": "進行中",
        "team": "チーム",
        "leaderboard": "ランキング",
        "next_up": "👀 次の試合",
        "time_up": "⏰ 時間終了！"
    },
    "中文": {
        "setup": "賽事設定",
        "format": "賽制選擇",
        "logic_play": "總分制",
        "logic_win": "搶分制",
        "logic_time": "限時制",
        "duration": "比賽時長 (分鐘)",
        "target": "目標分數",
        "courts": "球場數量",
        "generate": "🚀 生成對戰表",
        "confirm": "🎉 確認並下一輪",
        "finished": "已結束",
        "live": "進行中",
        "team": "隊伍",
        "leaderboard": "排行榜",
        "next_up": "👀 下一組預告",
        "time_up": "⏰ 時間到！"
    }
}

# --- 2. Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

if 'lang' not in st.session_state: st.session_state.lang = "中文"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'start_time' not in st.session_state: st.session_state.start_time = None

with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language", list(LANG_DICT.keys()))
    t = LANG_DICT[st.session_state.lang]
    st.divider()
    st.header(t["setup"])
    
    tourney_type = st.selectbox(t["format"], ["Americano", "Mexicano"])
    point_logic = st.selectbox("Logic", [t["logic_play"], t["logic_win"], t["logic_time"]])
    
    if point_logic == t["logic_time"]:
        game_duration = st.number_input(t["duration"], min_value=1, value=15)
        norm_target = st.number_input("Normalization Base", value=24)
        target = 999 
    else:
        st.subheader(t["target"])
        score_options = [12, 16, 20, 24, 32, "Custom"]
        selected_target = st.selectbox("Score", options=score_options, index=3)
        target = selected_target if selected_target != "Custom" else st.number_input("Value", min_value=1, value=24)
    
    num_p = st.number_input("Players", min_value=4, value=8, step=1)
    max_c = max(1, num_p // 4)
    num_c = st.selectbox(t["courts"], options=list(range(1, max_c + 1)), index=max_c-1)
    
    player_names = [st.sidebar.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"pin_{i}") for i in range(num_p)]
    
    if st.button(t["generate"], type="primary", use_container_width=True):
        valid_n = [n.strip() for n in player_names if n.strip()]
        random.shuffle(valid_n)
        st.session_state.players = pd.DataFrame({'Player': valid_n, 'Points': [0.0]*len(valid_n)})
        st.session_state.num_courts = num_c
        st.session_state.round = 1
        st.session_state.start_time = time.time()
        # 預生成下一輪順序
        next_n = valid_n.copy()
        random.shuffle(next_n)
        st.session_state.next_roster = next_n
        st.rerun()

# --- 4. Main Dashboard ---
if st.session_state.players is not None:
    st.title(f"{tourney_type} - Round {st.session_state.round}")
    
    # 頂部狀態欄 (時間 + 下一組預告)
    stat_l, stat_r = st.columns([2, 1])
    with stat_l:
        if point_logic == t["logic_time"] and st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            remaining = max(0, (game_duration * 60) - elapsed)
            mins, secs = divmod(int(remaining), 60)
            st.progress(remaining / (game_duration * 60))
            st.markdown(f"### ⏱️ {mins:02d}:{secs:02d}")
            if remaining <= 0: st.warning(t["time_up"])

    with stat_r:
        if tourney_type == "Americano" and 'next_roster' in st.session_state:
            with st.expander(t["next_up"], expanded=True):
                next_p = st.session_state.next_roster
                for c in range(st.session_state.num_courts):
                    st.caption(f"Court {string.ascii_uppercase[c]}: {next_p[c*4]} & {next_p[c*4+1]} vs {next_p[c*4+2]} & {next_p[c*4+3]}")

    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        roster = st.session_state.players['Player'].tolist()
        num_active = st.session_state.num_courts * 4
        active_players = roster[:num_active]
        all_done, scores_round = True, {}

        for i in range(st.session_state.num_courts):
            # 依你的圖示對齊 p1, p2 vs p3, p4
            p1, p2, p3, p4 = active_players[i*4 : i*4+4]
            s1_k, s2_k = f"s1_{i}_{st.session_state.round}", f"s2_{i}_{st.session_state.round}"
            if s1_k not in st.session_state: st.session_state[s1_k] = 0
            if s2_k not in st.session_state: st.session_state[s2_k] = 0
            
            s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
            is_done = (s1 + s2) >= target if t["logic_play"] in point_logic else (s1 >= target or s2 >= target)
            if point_logic == t["logic_time"]: is_done = (remaining <= 0)
            if not is_done: all_done = False

            with st.container(border=True):
                st.markdown(f"<div style='background-color:#ddd; color:black; text-align:center; font-weight:bold; margin-bottom:10px;'>COURT {string.ascii_uppercase[i]}</div>", unsafe_allow_html=True)
                
                total = s1 + s2
                srv_idx = (total // 4) % 4
                side_idx = total % 2 
                rotation = [p1, p3, p2, p4] # 發球順序

                c_l, c_m, c_r = st.columns([1, 1.2, 1])
                
                with c_l:
                    st.caption(f"TEAM 1")
                    for p in [p1, p2]:
                        bg = "#c6efce" if (not is_done and rotation[srv_idx] == p) else "#262730"
                        color = "black" if bg == "#c6efce" else "white"
                        st.markdown(f"<div style='border:1px solid #555; padding:5px; text-align:center; background-color:{bg}; color:{color};'>{p}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center; font-size:60px; margin:10px 0;'>{s1}</h1>", unsafe
