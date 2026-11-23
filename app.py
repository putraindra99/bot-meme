import streamlit as st
import urllib.request, json
import pandas as pd

st.set_page_config(page_title="MEME NAGA BIRU - PRO", page_icon="🐉", layout="wide")
st.title("🐉 MEME NAGA BIRU - PRO")
st.caption("Solana Trending - Update 10 detik")

if "cash" not in st.session_state:
    st.session_state.cash = 1000.0
    st.session_state.wins = 0
    st.session_state.losses = 0
    st.session_state.punya = None
    st.session_state.beli = 0
    st.session_state.jumlah = 0
    st.session_state.giliran = 0
    st.session_state.equity_hist = [1000.0]
    st.session_state.depo_hist = []
    st.session_state.running = True

@st.cache_data(ttl=10)
def ambil_coin():
    try:
        req = urllib.request.Request("https://api.dexscreener.com/latest/dex/search/?q=solana", headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            pairs = data.get("pairs", [])[:10]
            coins = []
            for p in pairs:
                coins.append({"nama": p.get("baseToken",{}).get("symbol","?"), "harga": float(p.get("priceUsd",0) or 0), "naik": float(p.get("priceChange",{}).get("h1",0) or 0)})
            if coins:
                return coins
    except:
        pass
    return [{"nama":"BONK","harga":0.00002,"naik":5.2},{"nama":"WIF","harga":1.2,"naik":-2.1},{"nama":"POPCAT","harga":0.85,"naik":8.4},{"nama":"MEW","harga":0.005,"naik":3.1},{"nama":"BOME","harga":0.008,"naik":-1.5}]

coins = ambil_coin()
idx = st.session_state.giliran % len(coins)
coin = coins[idx]
harga = coin["harga"] if coin["harga"] > 0 else 0.00001

nilai_posisi = st.session_state.jumlah * harga if st.session_state.punya == coin["nama"] else 0
equity = st.session_state.cash + nilai_posisi
if st.session_state.punya and st.session_state.punya != coin["nama"]:
    equity = st.session_state.cash + st.session_state.jumlah * st.session_state.beli
cuan = equity - 1000.0
st.session_state.equity_hist.append(equity)
if len(st.session_state.equity_hist) > 50:
    st.session_state.equity_hist = st.session_state.equity_hist[-50:]

c1,c2,c3,c4 = st.columns(4)
c1.metric("MODAL", "$1000")
c2.metric("CUAN", f"${cuan:,.2f}")
c3.metric("EQUITY", f"${equity:,.2f}")
c4.metric("MENANG / KALAH", f"{st.session_state.wins} / {st.session_state.losses}")
st.metric("CASH", f"${st.session_state.cash:,.2f}")

st.divider()
s1,s2,s3 = st.columns(3)
if s1.button("▶️ START BOT", use_container_width=True, type="primary"):
    st.session_state.running = True
    st.rerun()
if s2.button("⏸️ PAUSE BOT", use_container_width=True):
    st.session_state.running = False
if s3.button("🚨 EMERGENCY STOP - JUAL SEMUA", use_container_width=True):
    if st.session_state.punya:
        st.session_state.cash += st.session_state.jumlah * harga
        st.session_state.punya = None
        st.session_state.jumlah = 0
        st.rerun()

is_up = equity >= 1000
warna = "#00FF88" if is_up else "#FF3355"
st.subheader("📊 Grafik Equity - Hijau Naik, Merah Turun")
st.markdown(f"<h3 style='color:{warna}'>{'▲ NAIK - HIJAU' if is_up else '▼ TURUN - MERAH'} - Equity ${equity:,.2f}</h3>", unsafe_allow_html=True)
st.line_chart(pd.DataFrame({"Equity": st.session_state.equity_hist}), color=warna)

st.divider()
st.subheader("🏦 Deposit & Withdraw")
d1,d2 = st.columns(2)
with d1:
    dep = st.number_input("Deposit ($)", min_value=10.0, value=100.0, step=10.0, key="dep")
    if st.button("➕ Deposit Sekarang", use_container_width=True):
        st.session_state.cash += dep
        st.session_state.depo_hist.append(f"DEPOSIT +${dep:,.2f}")
        st.rerun()
with d2:
    wd = st.number_input("Withdraw ($)", min_value=10.0, value=100.0, step=10.0, key="wd")
    if st.button("➖ Withdraw Sekarang", use_container_width=True):
        if wd > st.session_state.cash:
            st.error("Cash tidak cukup!")
        else:
            st.session_state.cash -= wd
            st.session_state.depo_hist.append(f"WITHDRAW -${wd:,.2f}")
            st.rerun()

st.write("**Riwayat:**")
for h in reversed(st.session_state.depo_hist[-5:]):
    st.write(h)

st.divider()
st.subheader(f"🎯 Coin: {coin['nama']} - ${harga:.6f} - 1j: {coin['naik']:.2f}%")
if st.session_state.punya:
    st.info(f"Pegang: {st.session_state.punya} x {st.session_state.jumlah:.2f} | Beli ${st.session_state.beli:.6f}")
else:
    st.write("Belum pegang coin.")

b1,b2,b3 = st.columns(3)
if b1.button("🟢 BELI $50", use_container_width=True):
    if st.session_state.cash >= 50 and not st.session_state.punya:
        st.session_state.cash -= 50
        st.session_state.punya = coin["nama"]
        st.session_state.beli = harga
        st.session_state.jumlah = 50 / harga
        st.rerun()
if b2.button("🔴 JUAL SEMUA", use_container_width=True):
    if st.session_state.punya:
        hasil = st.session_state.jumlah * harga
        profit = hasil - 50
        st.session_state.cash += hasil
        if profit > 0:
            st.session_state.wins += 1
        else:
            st.session_state.losses += 1
        st.session_state.punya = None
        st.session_state.jumlah = 0
        st.rerun()
if b3.button("⏭️ GILIRAN BERIKUTNYA", use_container_width=True):
    st.session_state.giliran += 1
    st.rerun()
