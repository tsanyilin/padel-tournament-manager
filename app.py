import streamlit as st
import pandas as pd
import string
import random
import time

# --- 1. Translation Dictionary ---
LANG_DICT = {
    "English": {
        "setup": "Tennis Tournament Setup",
        "format": "Match Format",
        "logic_play": "Points to Play (Total)",
        "logic_win": "Points to Win",
        "logic_time": "Time Play",
        "duration": "Duration (Minutes)",
        "target": "Target Score",
        "courts": "Number of Tennis Courts",
        "generate": "🚀 GENERATE TABLE",
        "confirm": "🎉 CONFIRM & NEXT ROUND",
        "undo": "🔙 UNDO / GO BACK",
        "live": "LIVE MATCHES",
        "leaderboard": "Rankings",
        "next_up": "NEXT UP",
        "time_up": "⏰ TIME IS UP!",
        "history": "Match Results",
        "download": "📥 Download Tournament Report"
    },
    "日本語": {
        "setup": "テニス大会設定",
        "format": "試合形式",
        "logic_play": "総得点制",
        "logic_win": "勝利点制",
        "logic_time": "時間制",
        "duration": "試合時間 (分)",
        "target": "目標スコア",
        "courts": "コート数",
        "generate": "🚀 試合開始",
        "confirm": "🎉 確定して次へ",
        "undo": "🔙 前のラウンドに戻る",
        "live": "進行中",
        "leaderboard": "ランキング",
        "next_up": "次はこちら",
        "time_up": "⏰ 時間終了！",
        "history": "対戰紀錄",
        "download": "📥 CSVレポートをダウンロード"
    },
    "中文": {
        "setup": "網球賽事設定",
        "format": "賽制選擇",
        "logic_play": "總分制",
        "logic_win": "搶分制",
        "logic_time": "限時制",
        "duration": "比賽時長 (分鐘)",
        "target": "目標分數",
        "courts": "球場數量",
        "generate": "🚀 生成對戰表",
        "confirm": "🎉 確認並下一輪",
        "undo": "🔙 撤銷回上一輪",
        "live": "進行中",
        "leaderboard": "排行榜",
        "next_up": "下一組預告",
        "time_up": "⏰ 時間到！",
        "history": "對戰紀錄",
        "download": "📥 下載完整賽報 (CSV)"
    }
}

# --- 2. Configuration & Session State ---
st.set_page_config(page_title="Tennis Manager Pro", layout="wide", page_icon="🎾")

if 'lang' not in st.session_state: st.session_state.lang = "中文"
if 'players' not in st.session_state: st.session_state.players = None
if 'round' not in st.session_state: st.session_state.round = 1
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'history' not in st.session_state: st.session_state.history = []
if 'match_logs' not in st.session_state: st.session_state.match_logs = []
if 'player_list' not in st.session_state: st.session_state.player_list = [f"Player {i+1}" for i in range(8)]

# --- 3. Sidebar ---
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
        score_options = [12, 16, 20, 24, 32, "Custom"]
        selected_target = st.selectbox(t["target"], options=score_options, index=3)
        target = selected_target if selected_target != "Custom" else st.number_input("Value", min_value=1, value=24)
    
    st.subheader(f"👥 Players ({len(st.session_state.player_list)})")
    current_names = []
    for i, name in enumerate(st.session_state.player_list):
        c_in, c_del = st.columns([4, 1])
        with c_in:
            updated_name = st.text_input(f"P{i}", value=name, key=f"p_input_{i}", label_visibility="collapsed")
            current_names.append(updated_name)
        with c_del:
            if st.button("❌", key=f"del_{i}"):
                if len(st.session_state.player_list) > 4:
                    st.session_state.player_list.pop(i)
                    st.rerun()
    st.session_state.player_list = current_names

    if st.button("➕ Add Player", use_container_width=True):
        st.session_state.player_list.append(f"Player {len(st.session_state.player_list)+1}")
        st.rerun()

    st.divider()
    max_c = min(6, len(st.session_state.player_list) // 4)
    num_c_select = st.selectbox(t["courts"], options=list(range(1, max_c + 1)), index=max(0, max_c-1))
    
    if st.button(t["generate"], type="primary", use_container_width=True):
        valid_names = [n.strip() for n in st.session_state.player_list if n.strip()]
        random.shuffle(valid_names)
        
        # 歸零邏輯
        st.session_state.players = pd.DataFrame({'Player': valid_names, 'Points': [0.0]*len(valid_names)})
        st.session_state.num_courts = num_c_select
        st.session_state.round = 1
        st.session_state.start_time = time.time()
        st.session_state.history = []
        st.session_state.match_logs = []
        
        # 清除舊分
        for key in list(st.session_state.keys()):
            if key.startswith("s1_") or key.startswith("s2_"): del st.session_state[key]
        
        next_gen = valid_names.copy()
        random.shuffle(next_gen)
        st.session_state.next_roster = next_gen
        st.rerun()

# --- 4. Main Dashboard ---
if st.session_state.players is not None:
    st.title(f"🎾 {tourney_type} Tennis - Round {st.session_state.round}")
    
    tab_live, tab_hist = st.tabs([f"🎾 {t['live']}", f"📜 {t['history']}"])

    with tab_live:
        remaining_time = 0
        if point_logic == t["logic_time"] and st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            remaining_time = max(0, (game_duration * 60) - elapsed)
            mins, secs = divmod(int(remaining_time), 60)
            st.progress(remaining_time / (game_duration * 60))
            st.markdown(f"### ⏱️ {mins:02d}:{secs:02d}")
            if remaining_time <= 0: st.warning(t["time_up"])

        col_play, col_rank = st.columns([3, 1.2])

        with col_play:
            roster = st.session_state.players['Player'].tolist()
            num_active = st.session_state.num_courts * 4
            active_players = roster[:num_active]
            all_done = True

            for i in range(st.session_state.num_courts):
                p_set = active_players[i*4 : i*4+4]
                p1, p2, p3, p4 = p_set
                s1_k, s2_k = f"s1_{i}_{st.session_state.round}", f"s2_{i}_{st.session_state.round}"
                if s1_k not in st.session_state: st.session_state[s1_k] = 0
                if s2_k not in st.session_state: st.session_state[s2_k] = 0
                s1, s2 = st.session_state[s1_k], st.session_state[s2_k]
                
                is_done = (s1 + s2) >= target if t["logic_play"] in point_logic else (s1 >= target or s2 >= target)
                if point_logic == t["logic_time"]: is_done = (remaining_time <= 0)
                if not is_done: all_done = False

                with st.container(border=True):
                    st.markdown(f"<div style='background-color:#00712D; color:white; text-align:center; padding:3px; font-weight:bold;'>COURT {string.ascii_uppercase[i]}</div>", unsafe_allow_html=True)
                    total_pts = s1 + s2
                    srv_idx = (total_pts // 4) % 4
                    side_idx = total_pts % 2 
                    rotation = [p1, p3, p2, p4]
                    c_l, c_m, c_r = st.columns([1, 1.2, 1])
                    with c_l:
                        st.caption("TEAM 1")
                        for p in [p1, p2]:
                            bg = "#D4E157" if (not is_done and rotation[srv_idx] == p) else "#1E1E1E"
                            txt = "black" if bg == "#D4E157" else "white"
                            st.markdown(f"<div style='border:1px solid #444; padding:5px; text-align:center; background-color:{bg}; color:{txt}; font-size:13px; border-radius:4px;'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='text-align:center; font-size:55px; margin:5px 0;'>{s1}</h1>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("＋", key=f"a1_{i}", use_container_width=True, disabled=is_done): 
                            st.session_state[s1_k] += 1
                            st.rerun()
                        if b2.button("－", key=f"m1_{i}", use_container_width=True): 
                            st.session_state[s1_k] = max(0, s1-1)
                            st.rerun()
                    with c_m:
                        colors = ["#333"] * 4
                        if not is_done:
                            active = (2 if side_idx == 0 else 0) if srv_idx in [0, 2] else (1 if side_idx == 0 else 3)
                            colors[active] = "#D4E157"
                        st.markdown(f"""
                        <div style="display: grid; grid-template-columns: 1fr 6px 1fr; grid-template-rows: 55px 55px; border: 2px solid #555; background-color: #222; margin-top: 30px;">
                            <div style="background-color:{colors[0]}; border:0.5px solid #444;"></div>
                            <div style="grid-row:span 2; background-color:#555;"></div>
                            <div style="background-color:{colors[1]}; border:0.5px solid #444;"></div>
                            <div style="background-color:{colors[2]}; border:0.5px solid #444;"></div>
                            <div style="background-color:{colors[3]}; border:0.5px solid #444;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_r:
                        st.caption("TEAM 2")
                        for p in [p3, p4]:
                            bg = "#D4E157" if (not is_done and rotation[srv_idx] == p) else "#1E1E1E"
                            txt = "black" if bg == "#D4E157" else "white"
                            st.markdown(f"<div style='border:1px solid #444; padding:5px; text-align:center; background-color:{bg}; color:{txt}; font-size:13px; border-radius:4px;'>{p}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='text-align:center; font-size:55px; margin:5px 0;'>{s2}</h1>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("＋ ", key=f"a2_{i}", use_container_width=True, disabled=is_done): 
                            st.session_state[s2_k] += 1
                            st.rerun()
                        if b2.button("－ ", key=f"m2_{i}", use_container_width=True): 
                            st.session_state[s2_k] = max(0, s2-1)
                            st.rerun()

            if all_done:
                st.divider()
                col_confirm, col_undo = st.columns(2)
                with col_confirm:
                    if st.button(t["confirm"], type="primary", use_container_width=True):
                        snapshot = {"players": st.session_state.players.copy(), "round": st.session_state.round, "next_roster": st.session_state.next_roster.copy(), "courts_count": st.session_state.num_courts}
                        st.session_state.history.append(snapshot)
                        for j in range(st.session_state.num_courts):
                            p_active = active_players[j*4 : j*4+4]
                            sc1, sc2 = st.session_state[f"s1_{j}_{st.session_state.round}"], st.session_state[f"s2_{j}_{st.session_state.round}"]
                            st.session_state.match_logs.append({"Round": st.session_state.round, "Court": string.ascii_uppercase[j], "Team 1": f"{p_active[0]} & {p_active[1]}", "Score": f"{sc1} - {sc2}", "Team 2": f"{p_active[2]} & {p_active[3]}"})
                            if point_logic == t["logic_time"] and (sc1 + sc2) > 0:
                                ratio = norm_target / (sc1 + sc2)
                                sc1, sc2 = round(sc1 * ratio, 1), round(sc2 * ratio, 1)
                            for p in p_active[:2]: st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += sc1
                            for p in p_active[2:]: st.session_state.players.loc[st.session_state.players['Player'] == p, 'Points'] += sc2
                        st.session_state.players = st.session_state.players.set_index('Player').loc[st.session_state.next_roster].reset_index()
                        new_next = st.session_state.players['Player'].tolist()
                        random.shuffle(new_next)
                        st.session_state.next_roster = new_next
                        st.session_state.round += 1
                        st.session_state.start_time = time.time()
                        st.rerun()
                with col_undo:
                    if st.session_state.history:
                        if st.button(t["undo"], use_container_width=True):
                            last = st.session_state.history.pop()
                            st.session_state.players, st.session_state.round, st.session_state.next_roster = last["players"], last["round"], last["next_roster"]
                            st.session_state.match_logs = st.session_state.match_logs[:-last["courts_count"]]
                            st.rerun()

        with col_rank:
            # --- 排行榜修正區 ---
            st.subheader(f"🏆 {t['leaderboard']}")
            # 1. 複製目前的積分表並排序，同時重置 Index
            ranked_df = st.session_state.players.sort_values(by='Points', ascending=False).reset_index(drop=True)
            
            # 2. 修正：只針對前三名添加獎牌，不再覆蓋整欄
            if not ranked_df.empty:
                # 取得 'Player' 欄位的索引位置
                p_col_idx = ranked_df.columns.get_loc('Player')
                
                # 第一名 🥇
                ranked_df.iloc[0, p_col_idx] = f"{ranked_df.iloc[0, p_col_idx]} 🥇"
                # 第二名 🥈
                if len(ranked_df) > 1:
                    ranked_df.iloc[1, p_col_idx] = f"{ranked_df.iloc[1, p_col_idx]} 🥈"
                # 第三名 🥉
                if len(ranked_df) > 2:
                    ranked_df.iloc[2, p_col_idx] = f"{ranked_df.iloc[2, p_col_idx]} 🥉"
            
            st.dataframe(ranked_df, hide_index=True, use_container_width=True, height=500)

    with tab_hist:
        st.subheader(f"📜 {t['history']}")
        if st.session_state.match_logs:
            df_logs = pd.DataFrame(st.session_state.match_logs)
            st.dataframe(df_logs.iloc[::-1], hide_index=True, use_container_width=True)
            st.download_button(label=t["download"], data=df_logs.to_csv(index=False).encode('utf-8-sig'), file_name=f"tennis_report.csv", mime='text/csv')
        else: st.info("No records yet.")
else: st.info("👈 Please enter player names and start the tennis tournament from the sidebar.")
