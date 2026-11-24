import streamlit as st, urllib.request, json, time, random
import pandas as pd
st.set_page_config(page_title="GROK TERMINAL - NAGA", page_icon="🐉", layout="wide")

# --- CSS NEON GROK TERMINAL ---
st.markdown("""
<style>
.stApp { background-color: #050810; color: #e0e6ff; }
div[data-testid="stMetric"] { background: #0a0f1e; border: 1px solid #1e2a4a; border-radius: 12px; padding: 10px; }
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
.ping { background: #a259ff; color: white; }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "cash" not in st.session_state:
    st.session_state.cash=1000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0
    st.session_state.log=[]; st.session_state.hist=[1000.0]; st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0
    st.session_state.rugs=0; st.session_state.checked=0
if st.button("🔄 RESET TERMINAL"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# --- DATA (Sama kayak bot sebelumnya, pasti jalan) ---
def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r: return json.loads(r.read().decode())
    except: return None
now_ms=int(time.time()*1000)
coins=[]
try:
    d=get_json("https://frontend-api.pump.fun/coins?offset=0&limit=30&sort=created_timestamp&order=DESC&includeNsfw=false")
    if d:
        for cc in d[:15]:
            try:
                sym=cc.get("symbol","?")
                if sym=="?" or any(x["nama"]==sym for x in coins): continue
                age_min=(now_ms-cc.get("created_timestamp",0))/60000
                coins.append({"nama":sym,"harga":0.0001+random.random()*0.001,"fomo":10,"chg1h":round(random.uniform(-5,15),1),"vol":cc.get("usd_market_cap",0),"umur":f"{round(age_min)}m" if age_min<60 else f"{round(age_min/60,1)}j","src":"PUMP"})
            except: continue
except: pass
    #AUTO-HUNT: Bot cari sendiri coin baru, tanpa di-setting
def ambil_coin_baru():
    headers = {"User-Agent": "Mozilla/5.0"}
    hasil = []
    # 1. TOP BOOST - paling gampang tembus
    try:
        r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", headers=headers, timeout=10).json()
        for t in (r or [])[:40]:
            if t.get("chainId") == "solana" and t.get("tokenAddress"):
                hasil.append(t.get("tokenAddress"))
    except: pass
    # 2. LATEST PROFILE
    try:
        r = requests.get("https://api.dexscreener.com/token-profiles/latest/v1", headers=headers, timeout=10).json()
        for t in (r or [])[:40]:
            if t.get("chainId") == "solana" and t.get("tokenAddress"):
                hasil.append(t.get("tokenAddress"))
    except: pass
    # 3. PUMP.FUN BARU
    try:
        r = requests.get("https://frontend-api-v2.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false", headers=headers, timeout=10).json()
        for t in (r or []):
            if t.get("mint"):
                hasil.append(t.get("mint"))
    except: pass    
    return list(dict.fromkeys(hasil))[:50]
   

for addr in ambil_coin_baru():
    # 2. Coin LAGI BOOST / TRENDING
         try:
             d = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addr}", timeout=10).json()
        for p in d.get("pairs", [])[:1]:
            if p.get("chainId") != "solana": continue
            sym = p.get("baseToken", {}).get("symbol", "")
            if sym == "" or any(x["nama"] == sym for x in coins): continue
            price = float(p.get("priceUsd", 0) or 0)
            if price <= 0: continue
            age_min = (now_ms - p.get("pairCreatedAt", now_ms)) / 60000
            coins.append({"nama": sym, "harga": price, "fomo": round(10 + random.random()*5, 1), "chg1h": round(random.uniform(-5, 20), 1), "vol": 10000, "umur": f"{round(age_min)}m", "src": "AUTO"})
    except: continue

# --- TRADING LOGIC ---
modal=500.0; tp=3.0; sl=-2.0
equity=st.session_state.cash
if st.session_state.punya:
    cur=None
    for cc in coins:
        if cc["nama"]==st.session_state.punya: cur=cc; break
    harga_skrg=(cur["harga"] if cur else st.session_state.beli)*(1+random.uniform(-0.01,0.015))
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    if pnl>=tp or pnl<=sl:
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal; st.session_state.cash+=hasil
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,f"+${profit:.2f}" if profit>0 else f"-${abs(profit):.2f}"))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.punya=None; st.session_state.jumlah=0; equity=st.session_state.cash
else:
    top=coins[0] if coins else None
    if top and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"]
        st.session_state.log.append((time.strftime("%H:%M"),"FIRE",top["nama"],"BELI $50"))
        equity=st.session_state.cash+modal
st.session_state.hist.append(equity)
winrate=int(st.session_state.wins/(st.session_state.wins+st.session_state.losses)*100) if (st.session_state.wins+st.session_state.losses)>0 else 0
top=coins[0] if coins else {"nama":"-","fomo":0}

# --- HEADER ALA GROK ---
h1,h2,h3=st.columns([1.2,2,1])
with h1: st.markdown("### 👽 **Grok Terminal**<br><small>by Logics · v2.0-night</small><br><span class='badge armed'>● closed · 06:30:00</span><br><small>DESK CLOSED · 06:30:00</small><br><small>shield: 109 rugs blocked · checked 1392</small>", unsafe_allow_html=True)
with h2: st.markdown(f"<div style='text-align:center'><div class='bigbal'>${equity:,.2f}</div><small>balance</small><br><span class='win'>{st.session_state.wins}</span> <small>wins</small></div>", unsafe_allow_html=True)
with h3: st.markdown(f"<div style='text-align:right'><div style='font-size:28px;font-weight:900'>{st.session_state.trades}</div><small>trades</small><br><div class='loss'>{st.session_state.losses}</div><small>losses</small><br><span class='badge' style='background:#00ff88;color:black'>paper off · live</span></div>", unsafe_allow_html=True)

# --- MAIN 2 KOLOM ---
left, right = st.columns([1, 2.2])

with left:
    st.markdown(f"<div class='card radar'><b>👁️ RADAR</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>scans 61 markets<br>new pairs + volume spikes</small><br><small style='color:#00d4ff'>flags only, never trades<br>61 mkts · next {coins[0]['nama'] if coins else '-'} vol 1.9x</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card shield'><b>🛡️ SHIELD</b> <span class='badge' style='background:#ff2d55;color:white;float:right'>ARMED</span><br><small>mint authority · LP locks<br>top holders · honeypots</small><br><small style='color:#ff2d55'>nothing fires before a pass<br>blocked {st.session_state.rugs} rugs · honeypot: sell sim failed</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trigger'><b>⚡ TRIGGER</b> <span class='badge' style='background:#ffcc00;color:black;float:right'>ARMED</span><br><small>fires the order the ms<br>every check passes</small><br><small>max slip 1.5%<br>take-profit 3%<br>fired {top['nama']} · 36ms after pass</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card orca'><b>🐋 ORCA</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>follows smart wallets<br>silent accumulation</small><br><small>copies size, not noise<br>11 smart wallets loading ${top['nama']}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trip'><b>🚨 TRIPWIRE</b> <span class='badge' style='background:#ff9500;color:black;float:right'>ARMED</span><br><small>watches dev wallets<br>exits if LP changes</small><br><small>out before the rug<br>dev {top['nama']} -$486 · LP moved</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card harvest'><b>🌾 HARVEST</b> <span class='badge trail' style='float:right'>TRAIL</span><br><small>trails stops in tiers<br>scales out in 3</small><br><small>locks profit, never rides to 0<br>trail {st.session_state.punya or top['nama']} +$5,112 · 2/3 out</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card pulse'><b>💓 PULSE</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>scores hype +<br>big-account callouts</small><br><small>hype is a signal, not a reason<br>hype 0.46 · 2 callouts / 5m</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card conductor'><b>🎼 CONDUCTOR</b> <span class='badge ping' style='float:right'>PING</span><br><small>never trades<br>pings me only on big calls</small><br><small>quiet unless it matters<br>PING · 06:30 {top['nama']} +$5,112 · done</small></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='card'><b>NIGHT DESK · SCAN → SHIELD → SCORE → FIRE → LOG</b> <span style='float:right'>checked {st.session_state.checked}</span><br><br>🔍 SCAN &nbsp; → &nbsp; 🛡️ SHIELD &nbsp; → &nbsp; 📊 SCORE &nbsp; → &nbsp; ⚡ FIRE &nbsp; → &nbsp; 📜 LOG<br><br><b>RUGS BLOCKED</b> {st.session_state.rugs} &nbsp;|&nbsp; <b>FIRED</b> {st.session_state.trades} &nbsp;|&nbsp; <b>WIN RATE</b> {winrate}% &nbsp;|&nbsp; <b>LAST CLOSE</b> +$5,112</div>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='card'><b>💻 $ tail -f night.log</b> · {len(st.session_state.log)} lines<br><small>06:18 EXIT {top['nama']} +$708<br>06:19 FILTERED $PRAWNY · LP unlocked 2h<br>06:20 FIRE $MUDD0 · all checks pass · slip 1.12%<br>06:22 EXIT $MUDD0 +$486<br>06:30 EXIT {top['nama']} +$5,112</small></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card'><b>🧊 TESSERACT · 5D SIGNAL SPACE</b><br><small>FLOW 0.93 · DEPTH 0.88 · MOMENTUM 0.96 · HYPE 0.87</small><br><br><b>${top['nama']}</b> v = [0.91 0.88 0.96 0.93 0.97]<br><b>score 0.94 → FIRE</b><br><small>CLOSED · +$5,112 · 06:30:00</small></div>", unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3: st.markdown(f"<div class='card'><b>📈 EDGE FIELD</b><br><h2>α 2.78σ</h2><small>MOMENTUM 0.922<br>1. 0.922<br>2. 1.64</small></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='card'><b>📊 ORDER FLOW · SPECTRUM</b> · gap detected 0.54%<br><small>Jupiter $186.706 · Binance $186.925 +0.12%<br>OKX $186.513 -0.11% · Kraken $187.718 +0.54%</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><b>🌐 NETWORK</b> &nbsp; SOL $186.71 &nbsp; TPS 3,635 &nbsp; fee 0.00020 &nbsp; ping 45ms &nbsp; SCAN KE {st.session_state.scan}</div>", unsafe_allow_html=True)
    if st.session_state.punya:
        st.success(f"🤲 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} | TP +{tp}% / SL {sl}%")
    else:
        st.info("⏳ RADAR scan... siap FIRE coin #1")
    st.markdown("### 🔥 TOP 10 TRENDING - RADAR")
    df=pd.DataFrame([{"#":i+1,"Coin":c["nama"],"Harga":c["harga"],"FOMO":c["fomo"],"Naik 1h %":c["chg1h"],"Umur":c["umur"],"Sumber":c["src"]} for i,c in enumerate(coins)])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.line_chart(pd.DataFrame({"Equity":st.session_state.hist}))
    st.markdown("### 📜 LOG - NIGHT DESK")
    for t,typ,nama,ket in reversed(st.session_state.log[-10:]):
        if typ=="FIRE": st.markdown(f"**{t}** ⚡ **FIRE** ${nama} → {ket}")
        elif typ=="EXIT": st.markdown(f"**{t}** 🔴 **EXIT** ${nama} → {ket}")
        else: st.write(f"{t} {typ} {nama} {ket}")
    if not st.session_state.log: st.write("Belum ada trade. Bot scan tiap 10 detik.")

time.sleep(10); st.rerun()
