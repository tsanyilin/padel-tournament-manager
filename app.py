import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime, timedelta

# --- 1. Translation Dictionary ---
LANG_DICT = {
    "English": {
        "setup": "Tournament Setup", "logic_play": "Points to Play (Total)", "logic_win": "Points to Win",
        "logic_time": "Time Play", "target": "Target Score", "generate": "🚀 GENERATE",
        "confirm": "🎉 CONFIRM & NEXT", "finished": "FINISHED", "live": "LIVE", "team": "TEAM"
    },
    "日本語": {
        "setup": "大会設定", "logic_play": "総得点制", "logic_win": "勝利点制",
        "logic_time": "時間制", "target": "目標スコア", "generate": "🚀 試合開始",
        "confirm": "🎉 確定して次へ", "finished": "終了", "live": "進行中", "team": "チーム"
    },
    "Español": {
        "setup": "Configuración", "logic_play": "Puntos a Jugar", "logic_win": "Puntos para Ganar",
        "logic_time": "Tiempo de Juego", "target": "Objetivo", "generate": "🚀 GENERAR",
        "confirm": "🎉 CONFIRMAR Y SIGUIENTE", "finished": "FINALIZADO", "live": "EN JUEGO", "team": "EQUIPO"
    },
    "中文": {
        "setup": "賽事設定", "logic_play": "總分制", "logic_win": "搶分制",
        "logic_time": "限時制", "target": "目標分數", "generate": "🚀 生成對戰",
        "confirm": "🎉 確認並下一輪", "finished": "已結束", "live": "進行中", "team": "隊伍"
    }
}

# --- 2. Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'target_score' not in st.session_state: st.session_state.target_score = 24

# Sidebar Language Selector
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language", list(LANG_DICT.keys()))
    t = LANG_DICT[st.session_state.lang]

# --- 3. Sidebar Logic ---
with st.sidebar:
    st.divider()
    st.header(t["setup"])
    point_logic = st.selectbox("Logic", [t["logic_play"], t["logic_win"], t["logic_time"]])
    
    st.subheader(t["target"])
    score_cols = st.columns(3)
    for s in [12, 16, 20, 24, 32, "Custom"]:
        if score_cols[preset_scores.index(s)%3 if 'preset_scores' in locals() else 0].button(str(s), key=f"s_{s}"):
            st.session_state.target_score = s
    
    target = st.session_state.target_score if st.session_state.target_score != "Custom" else st.number_input("Pts", value=24)
    
    num_p = st.number_input("Players", min_value=4, value=8)
    player_names = [st.sidebar.text_input(f"P{i+1}", value=f"Player {i+1}", key=f"pi_{i}") for i in range(num_p)]
    
    if st.button(t["generate"], type="primary", use_container_width=True):
        valid = [n.strip() for n in player_names if n.strip()]
        random.shuffle(valid)
        st.session_state.players = pd.DataFrame({'Player': valid, 'Points': [0]*len(valid)})
        st.session_state.start_time = datetime.now()
        st.session_state.round = 1
        st.rerun()

# --- 4. Main UI ---
if st.session_state.players is not None:
    st.title(f"Round {st.session_state.round}")
    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        current_players = st.session_state.players['Player'].tolist()
        num_courts = len(current_players) // 4
        
        all_done, scores_round = True, {}

        for i in range(num_courts):
            p1, p2, p3, p4 = current_players[i*4 : i*4+4]
            s1_k, s2_k = f"s1_{i}_{st.session_state.round}", f"s2_{i}_{st.session_state.round}"
            
            if s1_k not in st.session_state: st.session_state[s1_k] = 0
            if s2_k not in st.session_state: st.session_state[s2_k] = 0
            
            s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
            is_done = (s1 + s2) >= target if t["logic_play"] in point_logic else (s1 >= target or s2 >= target)
            if not is_done: all_done = False

            with st.container(border=True):
                st.markdown(f"#### COURT {string.ascii_uppercase[i]} <span style='float:right;'>{t['finished'] if is_done else t['live']}</span>", unsafe_allow_html=True)
                
                # Service Logic
                total = s1 + s2
                srv_idx = (total // 4) % 4
                side_idx = total % 2 
                rotation = [p1, p3, p2, p4]

                c_l, c_m, c_r = st.columns([1, 1.5, 1])
                
                # --- TEAM 1 ---
                with c_l:
                    st.caption(f"{t['team']} 1")
                    for j, p in enumerate([p1, p2]):
                        bg = "#c6efce" if (not is_done and rotation[srv_idx] == p) else "transparent"
                        st.markdown(f"<div style='border:1px solid #555; padding:5px; text-align:center; background-color:{bg};'>{p}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center; margin:0;'>{s1}</h1>", unsafe_allow_html=True)
                    
                    if not is_done:
                        b_l, b_r = st.columns(2)
                        if b_l.button("＋", key=f"add1_{i}", use_container_width=True): 
                            st.session_state[s1_k] += 1; st.rerun()
                        if b_r.button("－", key=f"sub1_{i}", use_container_width=True): 
                            st.session_state[s1_k] = max(0, s1 - 1); st.rerun()

                # --- COURT VISUAL ---
                with c_mid:
                    colors = ["#333"] * 4
                    if not is_done:
                        # Correcting colors: Light green for active zone
                        active_idx = (2 if side_idx == 0 else 0) if srv_idx in [0, 2] else (1 if side_idx == 0 else 3)
                        colors[active_idx] = "#c6efce"
                    
                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 1fr 10px 1fr; grid-template-rows: 60px 60px; border: 2px solid #555; background-color: #222; margin: 10px auto; width: 90%;">
                        <div style="background-color:{colors[0]}; border:0.5px solid #444;"></div>
                        <div style="grid-row:span 2; background-color:#555;"></div>
                        <div style="background-color:{colors[1]}; border:0.5px solid #444;"></div>
                        <div style="background-color:{colors[2]}; border:0.5px solid #444;"></div>
                        <div style="background-color:{colors[3]}; border:0.5px solid #444;"></div>
                    </div>
                    """, unsafe_allow_html=True)

                # --- TEAM 2 ---
                with c_r:
                    st.caption(f"{t['team']} 2")
                    for j, p in enumerate([p3, p4]):
                        bg = "#c6efce" if (not is_done and rotation[srv_idx] == p) else "transparent"
                        st.markdown(f"<div style='border:1px solid #555; padding:5px; text-align:center; background-color:{bg};'>{p}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align:center; margin:0;'>{s2}</h1>", unsafe_allow_html=True)
                    
                    if not is_done:
                        b_l, b_r = st.columns(2)
                        if b_l.button("＋ ", key=f"add2_{i}", use_container_width=True): 
                            st.session_state[s2_k] += 1; st.rerun()
                        if b_r.button("－ ", key=f"sub2_{i}", use_container_width=True): 
                            st.session_state[s2_k] = max(0, s2 - 1); st.rerun()
                
                scores_round[p1] = s1; scores_round[p2] = s1
                scores_round[p3] = s2; scores_round[p4] = s2

        if all_done:
            if st.button(t["confirm"], type="primary", use_container_width=True):
                for p, s in scores_round.items():
                    st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += s
                st.session_state.round += 1
                st.rerun()

    with col_rank:
        st.subheader(t["leaderboard"])
        st.dataframe(st.session_state.players.sort_values(by='Points', ascending=False), hide_index=True)

else:
    st.info("👈 Please start the tournament from the sidebar.")
