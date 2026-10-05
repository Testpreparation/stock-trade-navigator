import pandas as pd
import streamlit as st
import yfinance as yf

# ページ基本設定
st.set_page_config(page_title="株式トレード判定ナビ", layout="wide")
st.title("📊 株式トレード判定ナビ（全自動取得版）")

# 1. サイドバー：設定エリア
st.sidebar.header("⚙️ 保有・目標設定")
symbol = st.sidebar.text_input("銘柄コード", value="6758.T")
stock_name = st.sidebar.text_input("銘柄名", value="ソニーグループ")
hold_shares = st.sidebar.number_input("保有株数", value=5, min_value=1)
avg_price = st.sidebar.number_input(
    "平均取得単価 (円)", value=3142.20, step=10.0
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 判定ライン")
buy_target = st.sidebar.number_input(
    "買い足し目標 (○円以下)", value=3400.0, step=10.0
)
sell_target = st.sidebar.number_input(
    "売り時・利確目標 (○円以上)", value=4300.0, step=10.0
)
stop_loss = st.sidebar.number_input(
    "損切り検討ライン (○円以下)", value=2900.0, step=10.0
)

# 2. 自動株価取得（yfinance）
ticker = yf.Ticker(symbol)
hist = ticker.history(period="1d")

if not hist.empty:
    current_price = round(hist["Close"].iloc[-1], 1)

    # 各種計算
    total_invested = avg_price * hold_shares
    current_total = current_price * hold_shares
    profit_loss = current_total - total_invested
    profit_rate = (profit_loss / total_invested) * 100

    # 3. 画面メイン表示
    st.subheader(f"📌 {stock_name} ({symbol}) のリアルタイム診断")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("現在株価（自動取得）", f"{current_price:,} 円")
    col2.metric("平均取得単価", f"{avg_price:,} 円")
    col3.metric(
        "評価損益",
        f"{profit_loss:+,} 円",
        delta=f"{profit_rate:+.2f}%",
    )
    col4.metric("保有評価額", f"{current_total:,} 円")

    st.markdown("---")

    # 4. 判定ロジック
    st.subheader("💡 総合判定結果")

    if current_price >= sell_target:
        st.success(
            f"🎉 **【売り時（利益確定）です】**\n\n"
            f"現在株価（{current_price}円）が利確ライン（{sell_target}円）に達しました！\n"
            f"手残り利益（概算）: **{int(profit_loss):,} 円**"
        )
    elif current_price <= stop_loss:
        st.error(
            f"⚠️ **【損切り検討エリアです】**\n\n"
            f"現在株価（{current_price}円）が撤退ライン（{stop_loss}円）を下回りました。"
        )
    elif current_price <= buy_target:
        add_shares = 5
        new_avg = round(
            (total_invested + (current_price * add_shares))
            / (hold_shares + add_shares),
            2,
        )
        st.warning(
            f"🛒 **【買い足し（買増し）チャンスです】**\n\n"
            f"現在株価（{current_price}円）が買い足しライン（{buy_target}円以下）に入りました。\n\n"
            f"・+{add_shares}株追加時の新平均単価: **{new_avg:,} 円**"
        )
    else:
        st.info(
            f"☕ **【継続保有（静観）モード】**\n\n"
            f"利確（{sell_target}円）まで あと **{round(sell_target - current_price, 1)}円**\n\n"
            f"買い足し（{buy_target}円）まで あと **{round(current_price - buy_target, 1)}円**"
        )

else:
    st.error("株価データの取得に失敗しました。銘柄コードを確認してください。")
