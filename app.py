import streamlit as st
import pandas as pd

# --- 基礎配置 ---
st.set_page_config(page_title="Padel Master", layout="wide")

# 初始化數據 (人數、積分等)
if 'players' not in st.session_state:
    st.session_state.players = None
if 'round' not in st.session_state:
    st.session_state.round = 1

# --- 側邊欄：功能設定 ---
with st.sidebar:
    st.title("🎾 比賽管理員")
    num_players = st.number_input("總人數", min_value=4, value=8, step=1)
    mode = st.radio("選擇模式", ["Mexicano (競技排位)", "Americano (社交輪轉)"])
    
    if st.button("初始化比賽", type="primary"):
        st.session_state.players = pd.DataFrame({
            '編號': [f"P{i+1}" for i in range(num_players)],
            '總積分': [0] * num_players,
            '場次': [0] * num_players
        })
        st.session_state.round = 1
        st.rerun()

    st.divider()
    st.markdown("### 🙌 支持開發")
    st.write("如果你喜歡這個工具，歡迎贊助一杯咖啡！")
    st.code("PayPay ID: tsanyilin")

# --- 主畫面邏輯 ---
if st.session_state.players is not None:
    st.header(f"第 {st.session_state.round} 輪 - {mode}")
    
    col_play, col_rank = st.columns([2, 1])

    with col_play:
        st.subheader("🔥 正在進行的對戰")
        # 這裡會根據模式產生不同的對戰邏輯 (Mexicano 依排名, Americano 依固定表)
        # 下方先以 Mexicano 為例展示計分介面
        sorted_list = st.session_state.players.sort_values(by='總積分', ascending=False)['編號'].tolist()
        
        # 簡單展示對戰 (假設兩場)
        for i in range(2):
            idx = i * 4
            if idx + 3 < len(sorted_list):
                st.info(f"Court {i+1}: {sorted_list[idx]} & {sorted_list[idx+1]} vs {sorted_list[idx+2]} & {sorted_list[idx+3]}")
                c1, c2 = st.columns(2)
                s1 = c1.number_input(f"C{i+1} 隊伍A 分數", min_value=0, key=f"s1_{i}")
                s2 = c2.number_input(f"C{i+1} 隊伍B 分數", min_value=0, key=f"s2_{i}")

        if st.button("提交比分並進入下一輪"):
            # 在這裡更新 st.session_state.players 的分數
            st.session_state.round += 1
            st.success("分數已更新！")

    with col_rank:
        st.subheader("🏆 全體成績排行")
        st.dataframe(st.session_state.players.sort_values(by='總積分', ascending=False), use_container_width=True)
else:
    st.info("請在左側選擇人數並點擊『初始化比賽』。")
