import streamlit as st
import urllib.request, json, random, time
import pandas as pd

st.set_page_config(page_title="BOT MEME", page_icon="🔥", layout="wide")

st.title("🔥 HUNTING MEME BOT")
st.caption("Solana Trending - Auto Giliran Coin - Update 10 detik")

if "cash" not in st.session_state:
    st.session_state.cash = 1000
    st.session_state.wins = 0
    st.session_state.losses = 0
    st.session_state.punya = None
    st.session_state.beli = 0
    st.session_state.jumlah = 0
    st.session_state.giliran = 0
    st.session_state.history = [1000]
    st.session_state.log = []

def ambil():
    try:
        req = urllib.request.Request("https://api.geckoterminal.com/api/v2/networks/solana/trending_pools", headers={"User-Agent":"Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        out=[]
        for d in data.get("data", [])[:10]:
            a=d.get("attributes",{})
            vol=float(a.get("volume_usd",{}).get("h24",0) or 0)
            harga=float(a.get("base_token_price_usd",0) or 0)
            if harga<=0: harga=vol/1000000
            out.append({"nama":a.get("name"),"vol":vol,"harga":harga})
        return out
    except:
        return []

coins = ambil()

if coins:
    if st.session_state.punya is None:
        pilihan = coins[st.session_state.giliran % len(coins)]
        st.session_state.giliran += 1
        st.session_state.punya = pilihan["nama"]
        st.session_state.beli = pilihan["harga"] * random.uniform(0.97, 1.03)
        pakai = st.session_state.cash * 0.5
        st.session_state.jumlah = pakai / st.session_state.beli
        st.session_state.cash -= pakai
        st.session_state.log.insert(0, f"BELI {pilihan['nama']}")
    else:
        harga_now = st.session_state.beli
        for c in coins:
            if c["nama"] == st.session_state.punya:
                harga_now = c["harga"] * random.uniform(0.97, 1.05)
                break
        profit = (harga_now - st.session_state.beli) / st.session_state.beli * 100
        if profit >= 3:
            st.session_state.cash += st.session_state.jumlah * harga_now
            st.session_state.wins += 1
            st.session_state.log.insert(0, f"JUAL UNTUNG {st.session_state.punya} +{profit:.1f}%")
            st.session_state.punya = None
        elif profit <= -2:
            st.session_state.cash += st.session_state.jumlah * harga_now
            st.session_state.losses += 1
            st.session_state.log.insert(0, f"JUAL RUGI {st.session_state.punya} {profit:.1f}%")
            st.session_state.punya = None

    equity = st.session_state.cash + (st.session_state.jumlah * st.session_state.beli if st.session_state.punya else 0)
    cuan = int(equity - 1000)
    st.session_state.history.append(int(equity))

    c1, c2, c3 = st.columns(3)
    c1.metric("MODAL", "$ 1,000")
    c2.metric("CUAN", f"$ {cuan:,}")
    c3.metric("EQUITY", f"$ {int(equity):,}")

    st.write(f"Status: {st.session_state.punya} | Menang: {st.session_state.wins} | Kalah: {st.session_state.losses} | Cash: $ {int(st.session_state.cash)} | Giliran ke-{st.session_state.giliran}")

    st.subheader("Grafik Equity")
    st.line_chart(pd.DataFrame(st.session_state.history, columns=["Equity"]))

    st.subheader("Top 10 Trending Solana")
    df = pd.DataFrame([{"Coin": c["nama"], "Volume 24h": f"$ {c['vol']:,.0f}", "Harga": f"$ {c['harga']:.5f}", "Status": "DIBELI" if c["nama"]==st.session_state.punya else ""} for c in coins])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Riwayat Jual Beli")
    for l in st.session_state.log[:10]:
        st.text(l)
else:
    st.warning("Lagi loading data...")

time.sleep(10)
st.rerun()
