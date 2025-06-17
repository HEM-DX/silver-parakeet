
#  streamlit run "c:/Users/J0134011/OneDrive - Honda/デスクトップ/シーラー管理/必要本数2app.py" --server.address 0.0.0.0
#  streamlit run 必要本数2app.py
#  streamlit run "c:/Users/J0134011/OneDrive - Honda/デスクトップ/シーラー管理/必要本数2app.py"

import streamlit as st
import pandas as pd
import math

st.title("使用量と必要本数シミュレーター")

file_path = r"C:\Users\J0134011\OneDrive - Honda\デスクトップ\シーラー管理\32Rk40.xlsx"

try:
    df = pd.read_excel(file_path, engine="openpyxl")
    df["使用量"] = df["使用量"].replace(" g", "", regex=True).astype(float)

    st.sidebar.header("⚙️ 設定")

    selected_processes = st.sidebar.multiselect(
        "工程を選択", options=df["工程"].unique(), default=list(df["工程"].unique())
    )
    operating_days = st.sidebar.number_input("稼働日数（生産日数）", min_value=1, value=20)
    production_units = st.sidebar.number_input("1日あたり生産台数", min_value=1, value=1100)
    drum_capacity = st.sidebar.number_input("ドラム缶容量 (kg)", min_value=1.0, value=250.0, step=10.0)
    split_days = st.sidebar.number_input("搬入の振り分け日数", min_value=1, value=15)

    filtered_df = df[df["工程"].isin(selected_processes)]

    per_unit = filtered_df.groupby("工程")["使用量"].sum().reset_index()
    per_unit.columns = ["工程", "1台あたり使用量（g）"]

    # 総使用量（kg） = 1台あたり使用量 × 生産台数 × 稼働日数 / 1000
    per_unit["総使用量（kg）"] = (
        per_unit["1台あたり使用量（g）"] * production_units * operating_days / 1000
    )

    # 必要ドラム缶数（切り上げ）
    per_unit["必要ドラム缶数"] = per_unit["総使用量（kg）"].apply(
        lambda x: math.ceil(x / drum_capacity)
    )

    # 合計使用量（kg）とドラム缶本数
    total_required_kg = per_unit["総使用量（kg）"].sum()
    total_drum_count = total_required_kg / drum_capacity
    daily_drum_count = total_drum_count / split_days

    # 表示用に単位付き列を追加
    per_unit_display = per_unit.copy()
    per_unit_display["総使用量（kg）"] = per_unit_display["総使用量（kg）"].map(lambda x: f"{x:.1f} kg")
    per_unit_display["必要ドラム缶数"] = per_unit_display["必要ドラム缶数"].astype(str) + " 本"

    # 表示
    st.subheader("📋 工程ごとの必要本数（kg）と必要ドラム缶数")
    st.dataframe(per_unit_display)

    st.subheader("📌 総使用量の合計と日別振り分け（ドラム缶本数）")
    st.markdown(f"✅ 全工程の必要本数 合計: **{total_drum_count:.1f} 本**")
    st.markdown(f"📅 {split_days}日（搬入日数）で振り分けた場合：**1日あたり {daily_drum_count:.1f} 本**")

    st.subheader("📊 グラフ：総使用量（kg）と必要ドラム缶数")
    st.bar_chart(per_unit.set_index("工程")[["総使用量（kg）", "必要ドラム缶数"]])

except FileNotFoundError:
    st.error("❌ Excelファイルが見つかりません。パスを確認してください。")
except Exception as e:
    st.error(f"⚠️ エラーが発生しました: {e}")
