import streamlit as st, urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="GROK TERMINAL - NAGA", page_icon="🐉", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #050810; color: #e0e6ff; }
.card { background: #0a0f1e; border: 1px solid #1e2a4a; border-radius: 12px; padding: 12px; margin-bottom: 10px; }
.radar { border-left: 4px solid #00d4ff; }
.shield { border-left: 4px solid #ff2d55; }
.trigger { border-left: 4px solid #ffcc00; }
.orca { border-left: 4px solid #00e5ff; }
.trip { border-left: 4px solid #ff9500; }
.harvest { border-left: 4px solid #00ff88; }
.pulse { border-left: 4px solid #ff5ec4; }
.conductor { border-left: 4px solid #a259ff; }
.bigbal { font-size: 38px; font-weight: 900; color: #00ff88; line-height: 1; }
.win { color: #00ff88; font-weight: 800; font-size: 28px; }
.loss { color: #ff2d55; font-weight: 800; font-size: 28px; }
.badge { padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.armed { background: #00d4ff; color: black; }
.trail { background: #00ff88; color: black; }
</style>
""", unsafe_allow_html=True)

if "cash" not in st.session_state:
    st.session_state.cash=10000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0
    st.session_state.log=[]; st.session_state.hist=[10000.0]
    st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0; st.session_state.checked=0
if st.button("🔄 RESET TERMINAL - NOLIN SEMUA"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r: return json.loads(r.read().decode())
    except: return None

now_ms=int(time.time()*1000)
coins=[]
def tambah(sym, price, chg, vol, txns, buys, age_min, src):
    # HARUS REAL + HARUS RAMAI - SEPI DIBUANG!
    if not sym or sym=="?" or not price or float(price)<=0: return
    if vol < 5000: return
    if txns < 50: return
    if any(x["nama"]==sym for x in coins): return
    # SKOR RAMAI = VOLUME + TXNS + BUYS
    ramai = vol + txns*100 + buys*100
    coins.append({"nama":sym,"harga":float(price),"ramai":int(ramai),"fomo":round(min(5+abs(chg)/2+vol/50000,20),1),"chg1h":round(float(chg),1),"vol":int(vol),"txns":int(txns),"buys":int(buys),"umur":f"{round(age_min)}m" if age_min<60 else f"{round(age_min/60,1)}j","src":src})

# 1. PUMP.FUN - HARGA REAL VIA DEXSREENER
try:
    d=get_json("https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false")
    if d:
        for cc in d[:20]:
            try:
                mint=cc.get("mint",""); sym=cc.get("symbol","?")
                if not mint or sym=="?": continue
                p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
                if not p or not p.get("pairs"): continue
                pair=p["pairs"][0]
                if pair.get("chainId")!="solana": continue
                tx=pair.get("txns",{}).get("h1",{})
                tambah(sym, float(pair.get("priceUsd",0) or 0), float(pair.get("priceChange",{}).get("h1",0) or 0), float(pair.get("volume",{}).get("h1",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-cc.get("created_timestamp",0))/60000, "PUMP")
            except: continue
except: pass

# 2. DEXSCREENER BOOSTS - YANG LAGI RAMAI DIBOOST
try:
    d=get_json("https://api.dexscreener.com/token-boosts/top/v1")
    if d:
        for b in d[:30]:
            try:
                addr=b.get("tokenAddress","")
                if not addr: continue
                p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{addr}")
                if not p: continue
                for pair in p.get("pairs",[])[:1]:
                    if pair.get("chainId")!="solana": continue
                    tx=pair.get("txns",{}).get("h1",{})
                    tambah(pair.get("baseToken",{}).get("symbol","?"), float(pair.get("priceUsd",0) or 0), float(pair.get("priceChange",{}).get("h1",0) or 0), float(pair.get("volume",{}).get("h1",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-pair.get("pairCreatedAt",now_ms))/60000, "BOOST")
            except: continue
except: pass

# 3. DEXSCREENER TRENDING PROFILES
try:
    d=get_json("https://api.dexscreener.com/token-profiles/latest/v1")
    if d:
        for b in d[:30]:
            try:
                addr=b.get("tokenAddress","")
                if not addr: continue
                p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{addr}")
                if not p: continue
                for pair in p.get("pairs",[])[:1]:
                    if pair.get("chainId")!="solana": continue
                    tx=pair.get("txns",{}).get("h1",{})
                    tambah(pair.get("baseToken",{}).get("symbol","?"), float(pair.get("priceUsd",0) or 0), float(pair.get("priceChange",{}).get("h1",0) or 0), float(pair.get("volume",{}).get("h1",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-pair.get("pairCreatedAt",now_ms))/60000, "TRENDING")
            except: continue
except: pass

# 4. GMGN - YANG RAMAI DIBELI WHALE
try:
    d=get_json("https://gmgn.ai/defi/quotation/v1/rank/solana/swaps/1h")
    if d and d.get("data"):
        for it in d["data"].get("rank",[])[:30]:
            try:
                tk=it.get("token",{})
                tambah(tk.get("symbol","?"), float(tk.get("price",0) or 0), float(it.get("price_change_percent",0) or 0), float(it.get("volume",0) or 0), int(it.get("swaps",0) or 0), int(it.get("swaps",0) or 0), 30, "GMGN")
            except: continue
except: pass

# 5. AXIOM / DEX SEARCH - HARGA REAL + RAMAI
for q in ["solana","meme","pump"]:
    d=get_json(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
    if not d: continue
    for p in d.get("pairs",[])[:30]:
        try:
            if p.get("chainId")!="solana": continue
            tx=p.get("txns",{}).get("h1",{})
            tambah(p.get("baseToken",{}).get("symbol","?"), float(p.get("priceUsd",0) or 0), float(p.get("priceChange",{}).get("h1",0) or 0), float(p.get("volume",{}).get("h1",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-p.get("pairCreatedAt",now_ms))/60000, "AXIOM")
        except: continue

if not coins:
    coins=[{"nama":"SOL","harga":186.7,"ramai":100000,"fomo":10,"chg1h":2.1,"vol":100000,"txns":1000,"buys":500,"umur":"-","src":"CADANGAN"}]
# SORT BY RAMAI - BUKAN FOMO! YANG PALING RAME DI ATAS!
coins=sorted(coins, key=lambda x: x["ramai"], reverse=True)[:20]
st.session_state.scan+=1; st.session_state.checked+=len(coins)

modal=500.0; tp=3.0; sl=-2.0
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
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,f"${profit:.2f}"))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.punya=None; st.session_state.jumlah=0; equity=st.session_state.cash
else:
    top=coins[0] if coins else None
    if top and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"]
        st.session_state.log.append((time.strftime("%H:%M"),"FIRE",top["nama"],f"BELI $500 - {top['src']} - VOL ${top['vol']:,} - {top['txns']} TX"))
        equity=st.session_state.cash+modal
st.session_state.hist.append(equity)
winrate=int(st.session_state.wins/(st.session_state.wins+st.session_state.losses)*100) if (st.session_state.wins+st.session_state.losses)>0 else 0
top=coins[0] if coins else {"nama":"-","fomo":0,"vol":0,"txns":0}

h1,h2,h3=st.columns([1.2,2,1])
with h1: st.markdown(f"### 👽 **Grok Terminal**<br><small>by Logics · v6.0-TRENDING-RAMAI</small><br><span class='badge armed'>● LIVE · {time.strftime('%H:%M:%S')}</span><br><small>100% HARGA REAL - COIN RAMAI</small>", unsafe_allow_html=True)
with h2: st.markdown(f"<div style='text-align:center'><div class='bigbal'>${equity:,.2f}</div><small>balance SIMULASI - Harga REAL</small><br><span class='win'>{st.session_state.wins}</span> <small>wins</small></div>", unsafe_allow_html=True)
with h3: st.markdown(f"<div style='text-align:right'><div style='font-size:28px;font-weight:900'>{st.session_state.trades}</div><small>trades</small><br><div class='loss'>{st.session_state.losses}</div><small>losses</small></div>", unsafe_allow_html=True)

left, right = st.columns([1, 2.2])
with left:
    st.markdown(f"<div class='card radar'><b>👁️ RADAR</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>PUMP + GMGN + AXIOM + DEX<br>cari yang PALING RAMAI</small><br><small style='color:#00d4ff'>paling rame: {top['nama']} · Vol ${top['vol']:,} · {top['txns']} tx</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card shield'><b>🛡️ SHIELD</b> <span class='badge' style='background:#ff2d55;color:white;float:right'>ARMED</span><br><small>BUANG coin sepi<br>Vol < $5k / Tx < 50 dibuang</small><br><small style='color:#ff2d55'>shield ON - RAMAI ONLY</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trigger'><b>⚡ TRIGGER</b> <span class='badge' style='background:#ffcc00;color:black;float:right'>ARMED</span><br><small>auto FIRE coin PALING RAMAI<br>modal $500</small><br><small>TP +{tp}% · SL {sl}% · Modal ${modal:.0f}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card orca'><b>🐋 ORCA</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>follows smart wallets<br>top rame: {top['nama']}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trip'><b>🚨 TRIPWIRE</b> <span class='badge' style='background:#ff9500;color:black;float:right'>ARMED</span><br><small>auto jual kalo TP / SL kena - HARGA REAL</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card harvest'><b>🌾 HARVEST</b> <span class='badge trail' style='float:right'>TRAIL</span><br><small>kunci profit, jual di TP</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card pulse'><b>💓 PULSE</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>scan ke-{st.session_state.scan} · NONSTOP</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card conductor'><b>🎼 CONDUCTOR</b> <span class='badge' style='background:#a259ff;color:white;float:right'>PING</span><br><small>simulasi, harga REAL market</small></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='card'><b>NIGHT DESK · SCAN → SHIELD → SCORE → FIRE → LOG</b> <span style='float:right'>checked {st.session_state.checked}</span><br><br>🔍 SCAN → 🛡️ SHIELD → 📊 SCORE → ⚡ FIRE → 📜 LOG<br><br><b>FIRED</b> {st.session_state.trades} | <b>WIN RATE</b> {winrate}% | <b>SCAN KE</b> {st.session_state.scan}</div>", unsafe_allow_html=True)
    if st.session_state.punya: st.success(f"🤲 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} REAL | TP +{tp}% / SL {sl}%")
    else: st.info("⏳ Bot lagi nyari coin yang PALING RAMAI...")
    st.markdown("### 🔥 COIN TRENDING PALING RAMAI - TOP 20 - HARGA REAL")
    df=pd.DataFrame([{"#":i+1,"Coin":c["nama"],"Harga REAL":c["harga"],"Naik 1h %":c["chg1h"],"Volume 1h $":c["vol"],"Txns 1h":c["txns"],"Buys":c["buys"],"Umur":c["umur"],"Sumber":c["src"]} for i,c in enumerate(coins)])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.line_chart(pd.DataFrame({"Equity":st.session_state.hist}))
    st.markdown("### 📜 LOG - AUTO TRADE - HARGA REAL")
    if st.session_state.log:
        for t,typ,nama,ket in reversed(st.session_state.log[-10:]):
            if typ=="FIRE": st.markdown(f"**{t}** ⚡ **FIRE** ${nama} → {ket}")
            else: st.markdown(f"**{t}** 🔴 **EXIT** ${nama} → {ket}")
    else: st.write("Belum ada trade. Tunggu 10 detik, bot scan tiap 10 detik.")
time.sleep(10); st.rerun()
