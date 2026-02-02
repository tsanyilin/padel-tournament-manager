import streamlit as st
import pandas as pd
import string
import random
import time
from datetime import datetime

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
        "generate": "🚀 GENERATE",
        "confirm": "🎉 CONFIRM & NEXT",
        "finished": "FINISHED",
        "live": "LIVE",
        "team": "TEAM",
        "leaderboard": "Leaderboard",
        "desc_ame": "🇺🇸 **Americano**: Random pairing each round. Social & Fun.",
        "desc_mex": "🇲🇽 **Mexicano**: Pairing by ranking (1&4 vs 2&3). Balanced & Competitive.",
        "time_up": "⏰ TIME IS UP!"
    },
    "日本語": {
        "setup": "大会設定",
        "format": "試合形式",
        "logic_play": "総得点制",
        "logic_win": "勝利点制",
        "logic_time": "時間制",
        "duration": "試合時間 (分)",
        "target": "目標スコア",
        "generate": "🚀 試合開始",
        "confirm": "🎉 確定して次へ",
        "finished": "終了",
        "live": "進行中",
        "team": "チーム",
        "leaderboard": "ランキング",
        "desc_ame": "🇺🇸 **Americano**: ラウンドごとに、ペアはランダム。交流重視。",
        "desc_mex": "🇲🇽 **Mexicano**: 順位でペア決定（1位&4位 vs 2位&3位）。実力均衡。",
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
        "generate": "🚀 生成對戰表",
        "confirm": "🎉 確認並下一輪",
        "finished": "已結束",
        "live": "進行中",
        "team": "隊伍",
        "leaderboard": "排行榜",
        "desc_ame": "🇺🇸 **Americano**: 隨機分配隊友，社交性質強。",
        "desc_mex": "🇲🇽 **Mexicano**: 排名配對（1&4 vs 2&3），實力平均。",
        "time_up": "⏰ 時間到！"
    }
}

# --- 2. Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

if 'lang' not in st.session_state: st.session_state.lang = "中文"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'target_score' not in st.session_state: st.session_state.target_score = 24
if 'start_time' not in st.session_state: st.session_state.start_time = None

# Language Selector
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language", list(LANG_DICT.keys()))
    t = LANG_DICT[st.session_state.lang]

# --- 3. Sidebar Configuration ---
with st.sidebar:
    st.divider()
    st.header(t["setup"])
    
    tourney_type = st.selectbox(t["format"], ["Americano", "Mexicano"])
    if tourney_type == "Americano": st.info(t["desc_ame"])
    else: st.info(t["desc_mex"])
        
    st.divider()
    
    point_logic = st.selectbox("Logic", [t["logic_play"], t["logic_win"], t["logic_time"]])
    
    # 邏輯判斷：如果是限時制，顯示時間設定，否則顯示分數設定
    if point_logic == t["logic_time"]:
        game_duration = st.number_input(t["duration"], min_value=1, value=15)
        target = 999 # 限時制下分數不設上限
    else:
        st.subheader(t["target"])
        preset_scores = [12, 16, 20, 24, 32, "Custom"]
        score_cols = st.columns(3)
        for idx, s in enumerate(preset_scores):
            if score_cols[idx % 3].button(str(s), key=f"score_btn_{s}", use_container_width=True):
                st.session_state.target_score = s
        target = st.session_state.target_score if st.session_state.target_score != "Custom" else st.number_input("Value", min_value=1, value=24)
    
    num_p = st.number_input("Players", min_value=4, value=8, step=4)
    player_names = [st.sidebar.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"pin_{i}") for i in range(num_p)]
    
    if st.button(t["generate"], type="primary", use_container_width=True):
        valid_n = [n.strip() for n in player_names if n.strip()]
        random.shuffle(valid_n)
        st.session_state.players = pd.DataFrame({'Player': valid_n, 'Points': [0]*len(valid_n)})
        st.session_state.round = 1
        st.session_state.start_time = time.time() # 記錄開始時間
        st.rerun()

# --- 4. Main Dashboard ---
if st.session_state.players is not None:
    st.title(f"{tourney_type} - Round {st.session_state.round}")
    
    # 時間制顯示倒數計時
    if point_logic == t["logic_time"] and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, (game_duration * 60) - elapsed)
        mins, secs = divmod(int(remaining), 60)
        
        st.progress(remaining / (game_duration * 60))
        st.subheader(f"⏱️ {mins:02d}:{secs:02d}")
        if remaining <= 0:
            st.warning(t["time_up"])

    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        # Mexicano 配對邏輯
        if tourney_type == "Mexicano" and st.session_state.round > 1:
            sorted_players = st.session_state.players.sort_values(by='Points', ascending=False)
            roster = sorted_players['Player'].tolist()
            new_roster = []
            for i in range(0, len(roster), 4):
                group = roster[i:i+4]
                if len(group) == 4: new_roster.extend([group[0], group[3], group[1], group[2]]) 
                else: new_roster.extend(group)
            roster = new_roster
        else:
            roster = st.session_state.players['Player'].tolist()

        num_courts = len(roster) // 4
        all_done, scores_round = True, {}

        for i in range(num_courts):
            p1, p2, p3, p4 = roster[i*4 : i*4+4]
            s1_k, s2_k = f"s1_{i}_{st.session_state.round}", f"s2_{i}_{st.session_state.round}"
            if s1_k not in st.session_state: st.session_state[s1_k] = 0
            if s2_k not in st.session_state: st.session_state[s2_k] = 0
            
            s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
            
            # 結束判定：分數制 或 時間到
            is_done = False
            if point_logic == t["logic_play"]: is_done = (s1 + s2) >= target
            elif point_logic == t["logic_win"]: is_done = (s1 >= target or s2 >= target)
            elif point_logic == t["logic_time"]: is_done = (remaining <= 0)
            
            if not is_done: all_done = False

            with st.container(border=True):
                st.markdown(f"#### COURT {string.ascii_uppercase[i]} <span style='float:right;'>{t['finished'] if is_done else t['live']}</span>", unsafe_allow_html=True)
                
                c_l, c_m, c_r = st.columns([1, 1, 1])
                with c_l:
                    st.caption(p1 + " & " + p2)
                    st.markdown(f"<h1 style='text-align:center;'>{s1}</h1>", unsafe_allow_html=True)
                    if not is_done:
                        if st.button("＋", key=f"a1_{i}"): st.session_state[s1_k] += 1; st.rerun()
                with c_m:
                    st.markdown("<div style='text-align:center; margin-top:30px;'>VS</div>", unsafe_allow_html=True)
                with c_r:
                    st.caption(p3 + " & " + p4)
                    st.markdown(f"<h1 style='text-align:center;'>{s2}</h1>", unsafe_allow_html=True)
                    if not is_done:
                        if st.button("＋ ", key=f"a2_{i}"): st.session_state[s2_k] += 1; st.rerun()
                
                scores_round[p1] = s1; scores_round[p2] = s1
                scores_round[p3] = s2; scores_round[p4] = s2

        if all_done:
            if st.button(t["confirm"], type="primary", use_container_width=True):
                for p, s in scores_round.items():
                    st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += s
                if tourney_type == "Americano":
                    current_players = st.session_state.players['Player'].tolist()
                    random.shuffle(current_players)
                    st.session_state.players = st.session_state.players.set_index('Player').loc[current_players].reset_index()
                st.session_state.round += 1
                st.session_state.start_time = time.time() # 重設下一輪時間
                st.rerun()
    
    # 排行榜... (省略重複部分)
