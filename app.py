import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime

# --- 1. Translation Dictionary ---
LANG_DICT = {
    "English": {
        "setup": "Tournament Setup",
        "format": "Tournament Format",
        "logic_play": "Points to Play (Total)",
        "logic_win": "Points to Win",
        "logic_time": "Time Play",
        "target": "Target Score",
        "generate": "🚀 GENERATE",
        "confirm": "🎉 CONFIRM & NEXT",
        "finished": "FINISHED",
        "live": "LIVE",
        "team": "TEAM",
        "leaderboard": "Leaderboard",
        "intro_title": "🎾 What are Americano & Mexicano?"
    },
    "日本語": {
        "setup": "大会設定",
        "format": "試合形式",
        "logic_play": "総得点制",
        "logic_win": "勝利点制",
        "logic_time": "時間制",
        "target": "目標スコア",
        "generate": "🚀 試合開始",
        "confirm": "🎉 確定して次へ",
        "finished": "終了",
        "live": "進行中",
        "team": "チーム",
        "leaderboard": "ランキング",
        "intro_title": "🎾 Americano と Mexicano の違い"
    },
    "中文": {
        "setup": "賽事設定",
        "format": "賽制選擇",
        "logic_play": "總分制",
        "logic_win": "搶分制",
        "logic_time": "限時制",
        "target": "目標分數",
        "generate": "🚀 生成對戰表",
        "confirm": "🎉 確認並下一輪",
        "finished": "已結束",
        "live": "進行中",
        "team": "隊伍",
        "leaderboard": "排行榜",
        "intro_title": "🎾 什麼是 Americano 與 Mexicano？"
    }
}

# --- 2. Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

if 'lang' not in st.session_state: st.session_state.lang = "中文"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'target_score' not in st.session_state: st.session_state.target_score = 24

# Language Selector
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language", list(LANG_DICT.keys()))
    t = LANG_DICT[st.session_state.lang]

# --- 3. Sidebar Configuration ---
with st.sidebar:
    st.divider()
    st.header(t["setup"])
    
    # 新增：賽制選擇 (Americano / Mexicano)
    tourney_type = st.selectbox(t["format"], ["Americano", "Mexicano"])
    
    point_logic = st.selectbox("Logic", [t["logic_play"], t["logic_win"], t["logic_time"]])
    
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
        # Americano 初始隨機，Mexicano 第一輪也通常是隨機
        random.shuffle(valid_n)
        st.session_state.players = pd.DataFrame({'Player': valid_n, 'Points': [0]*len(valid_n)})
        st.session_state.round = 1
        st.rerun()

    st.divider()
    # 要求的介紹區塊
    with st.expander(t["intro_title"]):
        if st.session_state.lang == "中文":
            st.markdown("""
            **🇺🇸 Americano (美式賽制)**
            - **核心：** 每一輪隨機配對。
            - **計分：** 每場打固定總分（如24分），13-11 則個人各拿 13 或 11 分。
            - **特色：** 社交性強，能跟所有人搭檔。

            **🇲🇽 Mexicano (墨式賽制)**
            - **核心：** 根據排名配對（強弱搭配）。
            - **邏輯：** 通常排名 1&4 vs 2&3，讓比賽更激烈平衡。
            - **特色：** 越打越刺激，實力越接近。
            """)
        else:
            st.markdown("Details about Americano and Mexicano formats...")

# --- 4. Main Dashboard ---
if st.session_state.players is not None:
    st.title(f"{tourney_type} - Round {st.session_state.round}")
    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        # 如果是 Mexicano 且不是第一輪，可以根據排名調整 roster
        if tourney_type == "Mexicano" and st.session_state.round > 1:
            sorted_players = st.session_state.players.sort_values(by='Points', ascending=False)
            roster = sorted_players['Player'].tolist()
            # 簡單 Mexicano 邏輯：1,4,2,3 一組 (Court A), 5,8,6,7 一組 (Court B)
            new_roster = []
            for i in range(0, len(roster), 4):
                group = roster[i:i+4]
                if len(group) == 4:
                    new_roster.extend([group[0], group[3], group[1], group[2]]) # 1&4 vs 2&3
                else:
                    new_roster.extend(group)
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
            is_done = (s1 + s2) >= target if t["logic_play"] in point_logic else (s1 >= target or s2 >= target)
            if not is_done: all_done = False

            with st.container(border=True):
                st.markdown(f"#### COURT {string.ascii_uppercase[i]} <span style='float:right;'>{t['finished'] if is_done else t['live']}</span>", unsafe_allow_html=True)
                
                total = s1 + s2
                srv_idx = (total // 4) % 4
                rotation = [p1, p3, p2, p4]

                c_l, c_m, c_r = st.columns([1, 1.5, 1])
                
                with c_l:
                    st.caption(f"{t['team']} 1")
                    for p in [p1, p2]:
                        bg = "#c6efce" if (not is_done and rotation[srv_idx] == p) else "transparent"
                        st.markdown(f"<div style='border:1px solid #555; padding:5px; text-align:center; background-color:{bg}; color:{'black' if bg != 'transparent' else 'white'};'>{p}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center;'>{s1}</h1>", unsafe_allow_html=True)
                    if not is_done:
                        b1, b2 = st.columns(2)
                        if b1.button("＋", key=f"a1_{i}", use_container_width=True): st.session_state[s1_k] += 1; st.rerun()
                        if b2.button("－", key=f"m1_{i}", use_container_width=True): st.session_state[s1_k] = max(0, s1-1); st.rerun()

                with c_m:
                    st.markdown(f"""<div style="height:120px; border:2px solid #555; background-color:#222; display:flex; align-items:center; justify-content:center; color:#555;">COURT</div>""", unsafe_allow_html=True)

                with c_r:
                    st.caption(f"{t['team']} 2")
                    for p in [p3, p4]:
                        bg = "#c6efce" if (not is_done and rotation[srv_idx] == p) else "transparent"
                        st.markdown(f"<div style='border:1px solid #555; padding:5px; text-align:center; background-color:{bg}; color:{'black' if bg != 'transparent' else 'white'};'>{p}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center;'>{s2}</h1>", unsafe_allow_html=True)
                    if not is_done:
                        b1, b2 = st.columns(2)
                        if b1.button("＋ ", key=f"a2_{i}", use_container_width=True): st.session_state[s2_k] += 1; st.rerun()
                        if b2.button("－ ", key=f"m2_{i}", use_container_width=True): st.session_state[s2_k] = max(0, s2-1); st.rerun()
                
                scores_round[p1] = s1; scores_round[p2] = s1
                scores_round[p3] = s2; scores_round[p4] = s2

        if all_done:
            if st.button(t["confirm"], type="primary", use_container_width=True):
                for p, s in scores_round.items():
                    st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += s
                
                # 如果是 Americano，下一輪前隨機打亂
                if tourney_type == "Americano":
                    current_players = st.session_state.players['Player'].tolist()
                    random.shuffle(current_players)
                    # 這裡簡單處理：直接重排 DataFrame 順序供下一輪讀取
                    st.session_state.players = st.session_state.players.set_index('Player').loc[current_players].reset_index()
                
                st.session_state.round += 1
                st.rerun()

    with col_rank:
        st.subheader(t["leaderboard"])
        st.dataframe(st.session_state.players.sort_values(by='Points', ascending=False), hide_index=True, use_container_width=True)

else:
    st.info("👈 Please start the tournament from the sidebar.")
