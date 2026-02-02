import streamlit as st
import pandas as pd
import string
import random
from datetime import datetime, timedelta

# --- 1. Translation Dictionary ---
LANG_DICT = {
    "English": {
        "title": "🎾 Padel Manager Pro",
        "setup": "Tournament Setup",
        "format": "Format",
        "logic": "Point Logic",
        "logic_play": "Points to Play (Total)",
        "logic_win": "Points to Win (First to X)",
        "logic_time": "Time Play (Personal Score)",
        "target": "Target Score",
        "players": "Player Setup",
        "num_p": "Total Players",
        "courts": "Courts",
        "duration": "Rental Duration (h)",
        "generate": "🚀 GENERATE TOURNAMENT",
        "round": "Current Round",
        "time_left": "Time Left",
        "live": "LIVE",
        "finished": "FINISHED",
        "leaderboard": "🏆 Leaderboard",
        "confirm": "🎉 CONFIRM & NEXT ROUND",
        "hurry": "Hurry up!",
        "team": "TEAM"
    },
    "日本語": {
        "title": "🎾 パデル・マネージャー",
        "setup": "大会設定",
        "format": "形式",
        "logic": "スコア方式",
        "logic_play": "総得点制 (Points to Play)",
        "logic_win": "勝利点制 (Points to Win)",
        "logic_time": "時間制 (個人スコア)",
        "target": "目標スコア",
        "players": "選手設定",
        "num_p": "参加人数",
        "courts": "コート数",
        "duration": "予約時間 (h)",
        "generate": "🚀 試合生成",
        "round": "現在のラウンド",
        "time_left": "残り時間",
        "live": "試合中",
        "finished": "終了",
        "leaderboard": "🏆 順位表",
        "confirm": "🎉 確定して次のラウンドへ",
        "hurry": "お急ぎください！",
        "team": "チーム"
    },
    "Français": {
        "title": "🎾 Padel Manager Pro",
        "setup": "Configuration du Tournoi",
        "format": "Format",
        "logic": "Logique de Points",
        "logic_play": "Points à Jouer (Total)",
        "logic_win": "Points pour Gagner",
        "logic_time": "Temps de Jeu (Score Perso)",
        "target": "Score Cible",
        "players": "Joueurs",
        "num_p": "Nombre de Joueurs",
        "courts": "Terrains",
        "duration": "Durée (h)",
        "generate": "🚀 GÉNÉRER LE TOURNOI",
        "round": "Tour Actuel",
        "time_left": "Temps Restant",
        "live": "EN COURS",
        "finished": "TERMINÉ",
        "leaderboard": "🏆 Classement",
        "confirm": "🎉 CONFIRMER & TOUR SUIVANT",
        "hurry": "Dépêchez-vous !",
        "team": "ÉQUIPE"
    },
    "中文": {
        "title": "🎾 Padel 賽事管理 Pro",
        "setup": "賽事設定",
        "format": "模式",
        "logic": "計分邏輯",
        "logic_play": "總分制 (Points to Play)",
        "logic_win": "搶分制 (Points to Win)",
        "logic_time": "限時制 (個人計分)",
        "target": "目標分數",
        "players": "選手名單",
        "num_p": "參賽人數",
        "courts": "場地數量",
        "duration": "場地時數 (h)",
        "generate": "🚀 生成對戰表",
        "round": "當前輪次",
        "time_left": "剩餘時間",
        "live": "進行中",
        "finished": "已結束",
        "leaderboard": "🏆 排行榜",
        "confirm": "🎉 確認結果並下一輪",
        "hurry": "時間快到了！",
        "team": "隊伍"
    }
}

# --- 2. Page Configuration ---
st.set_page_config(page_title="Padel Manager Pro", layout="wide", page_icon="🎾")

# Initialize Session State
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'target_score' not in st.session_state: st.session_state.target_score = 24

# Language Selection
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language / 言語 / Langue / 語言", list(LANG_DICT.keys()))
    t = LANG_DICT[st.session_state.lang] # Shorthand for translations

# --- 3. Sidebar Setup ---
with st.sidebar:
    st.divider()
    st.title(t["setup"])
    
    mode = st.radio(t["format"], ["Americano", "Mexicano"], horizontal=True)
    
    point_logic = st.selectbox(t["logic"], [t["logic_play"], t["logic_win"], t["logic_time"]])
    
    st.subheader(t["target"])
    score_cols = st.columns(3)
    preset_scores = [12, 16, 20, 24, 32, "Custom"]
    for idx, score in enumerate(preset_scores):
        if score_cols[idx % 3].button(str(score), key=f"btn_{score}", use_container_width=True):
            st.session_state.target_score = score

    target = st.session_state.target_score if st.session_state.target_score != "Custom" else st.number_input("Value", min_value=1, value=24)
    
    st.divider()
    st.subheader(t["players"])
    num_p = st.number_input(t["num_p"], min_value=4, value=8, step=1)
    player_names = []
    p_cols = st.columns(2)
    for i in range(num_p):
        name = p_cols[i % 2].text_input(f"P{i+1}", value=f"P{i+1}", key=f"p_in_{i}", label_visibility="collapsed")
        player_names.append(name)
    
    num_courts = st.number_input(t["courts"], min_value=1, value=num_p // 4)
    rental_hours = st.number_input(t["duration"], min_value=0.5, value=2.0, step=0.5)
    
    if st.button(t["generate"], type="primary", use_container_width=True):
        valid_names = [n.strip() for n in player_names if n.strip()]
        random.shuffle(valid_names)
        st.session_state.players = pd.DataFrame({
            'Player': valid_names, 'Points': [0] * len(valid_names), 'Matches': [0] * len(valid_names)
        })
        st.session_state.round = 1
        st.session_state.start_time = datetime.now()
        st.rerun()

# --- 4. Main Dashboard ---
if st.session_state.players is not None:
    # HH:MM Timer
    end_time = st.session_state.start_time + timedelta(hours=rental_hours)
    time_delta = end_time - datetime.now()
    total_sec = max(0, int(time_delta.total_seconds()))
    time_display = f"{total_sec // 3600:02d}:{(total_sec % 3600) // 60:02d}"

    m1, m2, m3 = st.columns(3)
    m1.metric(t["round"], f"{st.session_state.round}")
    m2.metric(t["target"], f"{target}")
    m3.metric(t["time_left"], time_display, delta=t["hurry"] if total_sec < 900 else None)

    st.divider()
    col_play, col_rank = st.columns([2.5, 1])

    with col_play:
        current_roster = st.session_state.players['Player'].tolist()
        on_court = current_roster[:num_courts * 4]
        all_done, scores_this_round = True, {}

        for i in range(num_courts):
            idx = i * 4
            if idx + 3 < len(on_court):
                p1, p2, p3, p4 = on_court[idx:idx+4]
                s1_k, s2_k = f"s1_{i}_{st.session_state.round}", f"s2_{i}_{st.session_state.round}"
                if s1_k not in st.session_state: st.session_state[s1_k] = 0
                if s2_k not in st.session_state: st.session_state[s2_k] = 0
                
                s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
                is_court_finished = (s1 + s2) >= target if t["logic_play"] in point_logic else (s1 >= target or s2 >= target)
                if not is_court_finished: all_done = False

                with st.container(border=True):
                    st.markdown(f"#### COURT {list(string.ascii_uppercase)[i]} <span style='float:right;'>{t['finished'] if is_court_finished else t['live']}</span>", unsafe_allow_html=True)
                    
                    # Server rotation logic
                    total = s1 + s2
                    rotation = [p1, p3, p2, p4] 
                    srv_idx = (total // 4) % 4
                    side_idx = total % 2 

                    cl, cm, cr = st.columns([1, 1.5, 1])
                    with cl: # Team 1
                        st.caption(f"{t['team']} 1")
                        for j, p in enumerate([p1, p2]):
                            is_srv = (srv_idx == (0 if j==0 else 2)) and not is_court_finished
                            st.markdown(f"<div style='border:1px solid #ddd; padding:5px; text-align:center; background-color:{'#c6efce' if is_srv else 'white'};'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='text-align:center;'>{s1}</h1>", unsafe_allow_html=True)
                        if not is_court_finished:
                            if st.button("＋", key=f"a1_{i}"): st.session_state[s1_k] += 1; st.rerun()

                    with cm: # Visual Court
                        colors = ["#f8f9fa"] * 4
                        if not is_court_finished:
                            if srv_idx in [0, 2]: colors[2 if side_idx == 0 else 0] = "#c6efce"
                            else: colors[1 if side_idx == 0 else 3] = "#c6efce"
                        st.markdown(f"""<div style="display: grid; grid-template-columns: 1fr 10px 1fr; grid-template-rows: 60px 60px; border: 2px solid black; background-color: white; margin: 10px auto; width: 90%;">
                            <div style="background-color:{colors[0]};"></div><div style="grid-row:span 2; background-color:#333;"></div>
                            <div style="background-color:{colors[1]};"></div><div style="background-color:{colors[2]};"></div><div style="background-color:{colors[3]};"></div>
                        </div>""", unsafe_allow_html=True)

                    with cr: # Team 2
                        st.caption(f"{t['team']} 2")
                        for j, p in enumerate([p3, p4]):
                            is_srv = (srv_idx == (1 if j==0 else 3)) and not is_court_finished
                            st.markdown(f"<div style='border:1px solid #ddd; padding:5px; text-align:center; background-color:{'#c6efce' if is_srv else 'white'};'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='text-align:center;'>{s2}</h1>", unsafe_allow_html=True)
                        if not is_court_finished:
                            if st.button("＋ ", key=f"a2_{i}"): st.session_state[s2_k] += 1; st.rerun()
                    
                    scores_this_round[p1], scores_this_round[p2] = s1, s1
                    scores_this_round[p3], scores_this_round[p4] = s2, s2

        if all_done:
            if st.button(t["confirm"], type="primary", use_container_width=True):
                for p, s in scores_this_round.items():
                    st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += s
                st.session_state.round += 1
                st.rerun()

    with col_rank:
        st.subheader(t["leaderboard"])
        st.dataframe(st.session_state.players.sort_values(by='Points', ascending=False), use_container_width=True, hide_index=True)

else:
    st.info("👈 Please complete setup in the sidebar.")
