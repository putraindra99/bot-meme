import streamlit as st, urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="NAGA GMGN TRENDING", page_icon="🐉", layout="wide")
st.title("🐉 NAGA BIRU - TRENDING GMGN / DEX / PUMP")
st.caption("SIMULASI Paper Trading | Umur 5m - 24j | Prioritas: Paling FOMO | Sama kayak di Aplikasi GMGN")

if "cash" not in st.session_state:
    st.session_state.cash=1000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0
    st.session_state.log=[]; st.session_state.hist=[1000.0]; st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0
if st.button("🔄 RESET BOT"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

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

# 1. DEXScreener Search - Trending Solana (Mirip GMGN)
for q in ["SOL","pump","meme","BONK"]:
    d=get_json(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
    if not d: continue
    for p in d.get("pairs",[])[:50]:
        try:
            if p.get("chainId")!="solana": continue
            sym=p.get("baseToken",{}).get("symbol","?")
            if sym=="?" or sym=="": continue
            price=float(p.get("priceUsd",0) or 0)
            if price<=0: continue
            age_min=(now_ms-p.get("pairCreatedAt",now_ms))/60000
            if age_min<5 or age_min>1440: continue
            if any(x["nama"]==sym for x in coins): continue
            chg5m=float(p.get("priceChange",{}).get("m5",0) or 0)
            chg1h=float(p.get("priceChange",{}).get("h1",0) or 0)
            vol1h=float(p.get("volume",{}).get("h1",0) or 0)
            tx=p.get("txns",{}).get("m5",{})
            buys=int(tx.get("buys",0) or 0); sells=int(tx.get("sells",0) or 0)
            fomo = min(vol1h/2000,15) + chg1h*0.8 + chg5m*1.0
            if buys+sells>0: fomo += (buys/(buys+sells))*10
            if age_min<60: fomo+=10
            elif age_min<360: fomo+=5
            coins.append({"nama":sym,"harga":price,"fomo":round(fomo,1),"chg5m":round(chg5m,1),"chg1h":round(chg1h,1),"vol":round(vol1h,0),"umur_txt":f"{round(age_min)}m" if age_min<60 else f"{round(age_min/60,1)}j","src":"DEX TREND"})
        except: continue

# 2. PUMP.FUN - Coin Baru (Harga dari MarketCap, di-skip kalo 0)
try:
    d=get_json("https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false")
    if d:
        for cc in d:
            try:
                sym=cc.get("symbol","?")
                if sym=="?" or sym=="": continue
                if any(x["nama"]==sym for x in coins): continue
                age_min=(now_ms-cc.get("created_timestamp",0))/60000
                if age_min<5 or age_min>1440: continue
                # Harga Pump.fun dari marketcap ga akurat, pake harga dummy biar bisa dibeli di simulasi
                # Kita skip yang ini kalo udah ada 10 coin dari DEX
                if len(coins)>=15: continue
                coins.append({"nama":sym,"harga":0.0001,"fomo":8,"chg5m":0,"chg1h":0,"vol":cc.get("usd_market_cap",0),"umur_txt":f"{round(age_min)}m","src":"PUMP.FUN"})
            except: continue
except: pass

# FILTER FINAL - Buang coin sampah ? dan harga 0
coins=[c for c in coins if c["nama"]!="?" and c["nama"]!="" and c["harga"]>0]
coins=sorted(coins, key=lambda x: x["fomo"], reverse=True)[:10]
st.session_state.scan+=1

# BUY / SELL OTOMATIS (SIMULASI)
equity=st.session_state.cash
if st.session_state.punya:
    cur=None
    for cc in coins:
        if cc["nama"]==st.session_state.punya: cur=cc; break
    harga_skrg=cur["harga"] if cur else st.session_state.beli
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    if pnl>=tp or pnl<=sl:
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal; st.session_state.cash+=hasil
        st.session_state.log.append(f"🔴 JUAL {st.session_state.punya} {pnl:.1f}% Profit ${profit:.2f} | {time.strftime('%H:%M:%S')}")
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.punya=None; st.session_state.jumlah=0; equity=st.session_state.cash
else:
    top=coins[0] if coins else None
    if top and top["fomo"]>2 and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"]
        st.session_state.log.append(f"🟢 BELI [{top['src']}] {top['nama']} ${modal:.0f} @ ${top['harga']:.6f} | FOMO {top['fomo']} | Umur {top['umur_txt']} | {time.strftime('%H:%M:%S')}")
        equity=st.session_state.cash+modal

st.session_state.hist.append(equity)
k1,k2,k3,k4=st.columns(4)
k1.metric("💰 CASH", f"${st.session_state.cash:,.2f}")
k2.metric("📈 EQUITY", f"${equity:,.2f}")
k3.metric("🔁 SCAN KE", st.session_state.scan)
k4.metric("🏆 W/L", f"{st.session_state.wins}W / {st.session_state.losses}L")
if st.session_state.punya: st.success(f"🤲 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} | TP +{tp}% / SL {sl}%")
else: st.info("⏳ Nunggu coin FOMO > 2...")

st.subheader("🔥 TOP 10 TRENDING - 5m SAMPAI 24 JAM (Sama kayak GMGN)")
if coins:
    df=pd.DataFrame([{"#":i+1,"Coin":c["nama"],"Harga":c["harga"],"FOMO":c["fomo"],"Naik 1h %":c["chg1h"],"Vol 1H $":c["vol"],"Umur":c["umur_txt"],"Sumber":c["src"]} for i,c in enumerate(coins)])
    st.dataframe(df, use_container_width=True, hide_index=True)
else: st.warning("DexScreener lagi lemot, nunggu 10 detik...")

st.line_chart(pd.DataFrame({"Equity":st.session_state.hist}))
st.subheader("📜 Log Auto Bot")
for h in reversed(st.session_state.log[-15:]): st.write(h)
if not st.session_state.log: st.write("Belum ada trade. Bot scan tiap 10 detik.")
time.sleep(10); st.rerun()
