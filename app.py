import streamlit as st, urllib.request, json, time, math
import pandas as pd
from datetime import datetime, timezone

st.set_page_config(page_title="NAGA GMGN 1 JAM", page_icon="🐉", layout="wide")
st.title("🐉 NAGA BIRU - GMGN + PUMP.FUN + DEX | 10m - 1h FOMO")
st.caption("Hanya coin umur 10 menit - 1 jam | Trending Pump.fun / GMGN / DexScreener | Bukan 24 jam")

# --- STATE ---
if "cash" not in st.session_state:
    st.session_state.cash=1000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0
    st.session_state.log=[]; st.session_state.hist=[1000.0]; st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0
    st.session_state.running=True

if st.button("🔄 RESET BOT"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# --- SETTING ---
c1,c2,c3=st.columns(3)
with c1: modal=st.number_input("Modal Beli ($)", value=50.0, step=10.0)
with c2: tp=st.number_input("Take Profit %", value=3.0)
with c3: sl=st.number_input("Stop Loss %", value=-2.0)

def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=8) as r: return json.loads(r.read().decode())
    except: return None

now_ms=int(time.time()*1000)
coins=[]

# 1. PUMP.FUN - Coin baru 1 jam terakhir
try:
    d=get_json("https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false")
    if d:
        for c in d:
            try:
                created=c.get("created_timestamp",0)
                age_min=(now_ms-created)/60000
                if age_min<10 or age_min>60: continue # CUMA 10m - 1 JAM
                price=c.get("usd_market_cap",0)
                # FOMO dari marketcap naik + umur muda
                fomo = 20 - abs(age_min-30)/3  # Paling FOMO umur 30 menitan
                if c.get("usd_market_cap",0)>5000: fomo+=5
                coins.append({"nama":c.get("symbol","?"), "harga":float(c.get("usd_market_cap",0) or 0)/1000000, "fomo":fomo, "chg5m":0, "vol":c.get("usd_market_cap",0), "umur":round(age_min,1), "src":"PUMP.FUN", "mint":c.get("mint","")})
            except: continue
except: pass

# 2. DEXScreener - Trending Solana, filter umur pair 10m-1jam
for q in ["pump","sol","meme"]:
    d=get_json(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
    if not d: continue
    for p in d.get("pairs",[])[:30]:
        try:
            if p.get("chainId")!="solana": continue
            created=p.get("pairCreatedAt",0)
            age_min=(now_ms-created)/60000
            if age_min<10 or age_min>60: continue # CUMA 10m - 1 JAM, BUKAN 24 JAM
            chg5m=float(p.get("priceChange",{}).get("m5",0) or 0)
            chg1h=float(p.get("priceChange",{}).get("h1",0) or 0)
            vol5m=float(p.get("volume",{}).get("m5",0) or 0)
            vol1h=float(p.get("volume",{}).get("h1",0) or 0)
            txns=p.get("txns",{}).get("m5",{})
            buys=int(txns.get("buys",0) or 0); sells=int(txns.get("sells",0) or 0)
            # FOMO 10m-1jam: Naik 5m + Volume 1 jam + Buy lebih banyak dari Sell
            fomo = chg5m*1.5 + chg1h*0.5 + min(vol1h/1000,10)
            if buys>sells and buys>0: fomo += (buys/(buys+sells))*10
            if vol5m>5000: fomo+=5
            sym=p.get("baseToken",{}).get("symbol","?")
            # Hindari duplikat
            if any(x["nama"]==sym for x in coins): continue
            coins.append({"nama":sym, "harga":float(p.get("priceUsd",0) or 0), "fomo":round(fomo,1), "chg5m":round(chg5m,1), "vol":round(vol1h,0), "umur":round(age_min,1), "src":"DEX 1H", "mint":p.get("baseToken",{}).get("address","")})
        except: continue

# 3. GMGN - Trending Solana 1 jam
d=get_json("https://gmgn.ai/api/v1/tokens/trending/sol?limit=50&timeframe=1h")
if d and isinstance(d,dict):
    for t in d.get("data",[])[:30]:
        try:
            sym=t.get("symbol","?")
            if any(x["nama"]==sym for x in coins): continue
            chg1h=float(t.get("price_change_1h",0) or 0)
            vol=float(t.get("volume_1h",0) or 0)
            fomo=chg1h*1.2 + min(vol/1000,10)
            coins.append({"nama":sym, "harga":float(t.get("price",0) or 0), "fomo":round(fomo,1), "chg5m":round(chg1h,1), "vol":round(vol,0), "umur":30, "src":"GMGN 1H", "mint":t.get("address","")})
        except: continue

# Sort by FOMO 1 JAM
coins=sorted(coins, key=lambda x: x["fomo"], reverse=True)[:10]
st.session_state.scan+=1

# --- AUTO BUY / SELL ---
log_box=st.empty()
equity=st.session_state.cash
if st.session_state.punya:
    # Cari harga terbaru coin yang dipegang
    cur=None
    for c in coins:
        if c["nama"]==st.session_state.punya: cur=c; break
    harga_skrg=cur["harga"] if cur else st.session_state.beli
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl_pct=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    # JUAL
    if pnl_pct>=tp or pnl_pct<=sl:
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal
        st.session_state.cash+=hasil
        st.session_state.log.append(f"🔴 JUAL {st.session_state.punya} {pnl_pct:.1f}% Profit ${profit:.2f} | {time.strftime('%H:%M:%S')}")
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1
        st.session_state.punya=None; st.session_state.jumlah=0
        equity=st.session_state.cash
else:
    # BELI - Syarat baru: FOMO > 5, Umur 10-60 menit, BUKAN 24 jam
    top=coins[0] if coins else None
    if top and top["fomo"]>5 and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"] if top["harga"]>0 else 0
        st.session_state.log.append(f"🟢 BELI [{top['src']}] {top['nama']} ${modal:.0f} @ ${top['harga']:.6f} | FOMO {top['fomo']} | Umur {top['umur']}m | {time.strftime('%H:%M:%S')}")
        equity=st.session_state.cash + modal

st.session_state.hist.append(equity)

# --- UI ---
k1,k2,k3,k4=st.columns(4)
k1.metric("💰 CASH", f"${st.session_state.cash:,.2f}")
k2.metric("📈 EQUITY", f"${equity:,.2f}")
k3.metric("🔁 SCAN KE", st.session_state.scan)
k4.metric("🏆 W/L", f"{st.session_state.wins}W / {st.session_state.losses}L")
if st.session_state.punya:
    st.success(f"🤲 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} | TP +{tp}% / SL {sl}%")
else:
    st.info("⏳ Nunggu coin umur 10m-1jam yang FOMO > 5...")

st.subheader("🔥 TOP 10 - UMUR 10 MENIT - 1 JAM (BUKAN 24 JAM)")
if coins:
    df=pd.DataFrame([{"#":i+1,"Coin":c["nama"],"Harga":c["harga"],"FOMO 1H":c["fomo"],"Naik 5m/1h %":c["chg5m"],"Vol 1H $":c["vol"],"Umur":f"{c['umur']}m","Sumber":c["src"]} for i,c in enumerate(coins)])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("Ga ada coin umur 10m-1jam yang trending sekarang, nunggu 10 detik lagi... Pump.fun lagi sepi")

st.line_chart(pd.DataFrame({"Equity":st.session_state.hist}))
st.subheader("📜 Log Auto Bot")
for h in reversed(st.session_state.log[-15:]): st.write(h)
if not st.session_state.log: st.write("Belum ada trade. Bot scan tiap 10 detik.")

time.sleep(10); st.rerun()
