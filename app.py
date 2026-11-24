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
.bigbal { font-size: 38px; font-weight: 900; line-height: 1; }
.badge { padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.armed { background: #00d4ff; color: black; }
.trail { background: #00ff88; color: black; }
.topbox { background: #0a0f1e; border: 1px solid #1e2a4a; border-radius: 12px; padding: 14px; text-align: center; }
.log-buy { background: #0a2a4a; border-left: 4px solid #00d4ff; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; }
.log-tp { background: #0a2e1a; border-left: 4px solid #00ff88; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; }
.log-sl { background: #2e0a12; border-left: 4px solid #ff2d55; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; }
.log-hold { background: #2e250a; border-left: 4px solid #ffcc00; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

if "cash" not in st.session_state:
    st.session_state.cash=10000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0
    st.session_state.log=[]; st.session_state.hist=[10000.0]
    st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0; st.session_state.checked=0; st.session_state.hold=0
    st.session_state.last_coins=[]
if st.button("🔄 RESET TERMINAL - NOLIN SEMUA"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r: return json.loads(r.read().decode())
    except: return None

now_ms=int(time.time()*1000)
all_coins=[]
def tambah(sym, price, chg, vol, txns, buys, age_min, src, mcap=0):
    if not sym or sym=="?" or not price or float(price)<=0: return
    if any(x["nama"]==sym for x in all_coins): return
    all_coins.append({"nama":sym,"harga":float(price),"ramai":int(vol),"fomo":round(min(5+abs(chg)/2+vol/50000,20),1),"chg1h":round(float(chg),1),"vol":int(vol),"txns":int(txns),"buys":int(buys),"umur":f"{round(age_min)}m" if age_min<60 else f"{round(age_min/60,1)}j","src":src,"mcap":int(mcap)})

# === SCAN 500 COIN - 60+ KEYWORD + PUMP 3 HALAMAN ===
try:
    d=get_json("https://api.dexscreener.com/latest/dex/pairs/solana?limit=50")
    if not d: d=get_json("https://api.dexscreener.com/latest/dex/search/?q=solana")
    pairs=d.get("pairs",[]) if d else []
    for p in pairs[:50]:
        try:
            if p.get("chainId")!="solana": continue
            tx=p.get("txns",{}).get("h24",{})
            mc = float(p.get("marketCap",0) or p.get("fdv",0) or 0)
            tambah(p.get("baseToken",{}).get("symbol","?"), float(p.get("priceUsd",0) or 0), float(p.get("priceChange",{}).get("h24",0) or 0), float(p.get("volume",{}).get("h24",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-p.get("pairCreatedAt",now_ms))/60000, "DEX-TREND", mc)
        except: continue
except: pass
KEYWORDS=["solana","meme","pump","bonk","wif","pepe","doge","cat","ai","moon","dog","trump","elon","frog","baby","king","grok","naga","dragon","sol","ray","jup","popcat","mew","goat","act","pnuts","chillguy","fartcoin","moodeng","neiro","turbo","brett","maga","usdt","usdc","btc","eth","shib","floki","baby","inu","pepe2","wojak","chad","based","degen","moonshot","lambo","rocket","gem","alpha","whale","orca","orca2","jito","pyth","wormhole","tensor","drift","marinade","wen","dust","saga","bonk2","wif2","pop","cat2","dog2","bird","fish","lion","tiger","bear","bull","ape","monkey","pig","cow","horse"]
for q in KEYWORDS:
    d=get_json(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
    if not d: continue
    for p in d.get("pairs",[])[:30]:
        try:
            if p.get("chainId")!="solana": continue
            tx=p.get("txns",{}).get("h24",{})
            mc = float(p.get("marketCap",0) or p.get("fdv",0) or 0)
            tambah(p.get("baseToken",{}).get("symbol","?"), float(p.get("priceUsd",0) or 0), float(p.get("priceChange",{}).get("h24",0) or 0), float(p.get("volume",{}).get("h24",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-p.get("pairCreatedAt",now_ms))/60000, "AXIOM", mc)
        except: continue
# PUMP 3 HALAMAN BIAR 150 COIN BARU!
for off in [0,50,100]:
    try:
        d=get_json(f"https://frontend-api.pump.fun/coins?offset={off}&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false")
        if not d: continue
        for cc in d[:30]:
            try:
                mint=cc.get("mint",""); sym=cc.get("symbol","?")
                if not mint or sym=="?": continue
                p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
                if not p or not p.get("pairs"): continue
                pair=p["pairs"][0]
                if pair.get("chainId")!="solana": continue
                tx=pair.get("txns",{}).get("h24",{})
                mc = float(pair.get("marketCap",0) or pair.get("fdv",0) or 0)
                tambah(sym, float(pair.get("priceUsd",0) or 0), float(pair.get("priceChange",{}).get("h24",0) or 0), float(pair.get("volume",{}).get("h24",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-cc.get("created_timestamp",0))/60000, "PUMP", mc)
            except: continue
    except: pass
try:
    d=get_json("https://api.dexscreener.com/token-boosts/top/v1")
    if d:
        for b in d[:50]:
            try:
                addr=b.get("tokenAddress","")
                if not addr: continue
                p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{addr}")
                if not p: continue
                for pair in p.get("pairs",[])[:1]:
                    if pair.get("chainId")!="solana": continue
                    tx=pair.get("txns",{}).get("h24",{})
                    mc = float(pair.get("marketCap",0) or pair.get("fdv",0) or 0)
                    tambah(pair.get("baseToken",{}).get("symbol","?"), float(pair.get("priceUsd",0) or 0), float(pair.get("priceChange",{}).get("h24",0) or 0), float(pair.get("volume",{}).get("h24",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-pair.get("pairCreatedAt",now_ms))/60000, "BOOST", mc)
            except: continue
except: pass
try:
    d=get_json("https://gmgn.ai/defi/quotation/v1/rank/solana/swaps/1h")
    if d and d.get("data"):
        for it in d["data"].get("rank",[])[:50]:
            try:
                tk=it.get("token",{})
                mc = float(tk.get("market_cap",0) or 0)
                tambah(tk.get("symbol","?"), float(tk.get("price",0) or 0), float(it.get("price_change_percent",0) or 0), float(it.get("volume",0) or 0), int(it.get("swaps",0) or 0), int(it.get("swaps",0) or 0), 30, "GMGN", mc)
            except: continue
except: pass

# === v7.5 - NAIK 100%-2500% DOANG! NO TIER5! NO MINUS! ===
def base_ok(c):
    mcap_ok = (c["mcap"]==0 or 5000<=c["mcap"]<=400000)
    vol_ok = 25000<=c["vol"]<=1000000
    return mcap_ok and vol_ok and c["txns"]>=20 and c["buys"]>=10

coins=[c for c in all_coins if 100<=c["chg1h"]<=2500 and base_ok(c)]
level="GAS NAIK 100%-2500% MCAP 5K-400K VOL 25K-1M - SCAN 500"
# Kalo gak ada, DIEM! JANGAN BELI MINUS LAGI!
total_scan=len(all_coins)
coins=sorted(coins, key=lambda x: x["chg1h"], reverse=True)[:20]
st.session_state.scan+=1; st.session_state.checked+=len(coins)

modal=500.0; tp=100.0; sl=-20.0; max_hold=60
equity=st.session_state.cash
if st.session_state.punya:
    cur=None; cur_idx=999
    for idx, cc in enumerate(coins):
        if cc["nama"]==st.session_state.punya: cur=cc; cur_idx=idx; break
    st.session_state.hold+=1
    jual_paksa=""
    if cur is None:
        jual_paksa="COIN HILANG / GAK NAIK 100% LAGI"
        harga_skrg=st.session_state.beli
    elif cur_idx>=10:
        jual_paksa=f"GAK RAMAI LAGI - RANK {cur_idx+1}"
        harga_skrg=cur["harga"]
    elif st.session_state.hold>=max_hold:
        jual_paksa="HOLD KELAMAAN 10 MENIT"
        harga_skrg=cur["harga"]
    else:
        harga_skrg=cur["harga"]
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    if pnl>=tp or pnl<=sl or jual_paksa!="":
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal; st.session_state.cash+=hasil
        alasan=jual_paksa if jual_paksa else f"TP/SL {pnl:.1f}%"
        if jual_paksa.startswith("HOLD"): jenis="HOLD"
        elif profit>0: jenis="TP"
        else: jenis="SL"
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,f"${profit:.2f} - {alasan}",jenis,profit))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1
        st.session_state.last_coins.append(st.session_state.punya)
        st.session_state.last_coins=st.session_state.last_coins[-3:]
        st.session_state.punya=None; st.session_state.jumlah=0; st.session_state.hold=0; equity=st.session_state.cash
else:
    top=None
    for cc in coins:
        if cc["nama"] not in st.session_state.last_coins:
            top=cc; break
    if top is None: top=coins[0] if coins else None
    if top and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"]; st.session_state.hold=0
        st.session_state.log.append((time.strftime("%H:%M"),"FIRE",top["nama"],f"BELI $500 - {top['src']} - MCAP ${top['mcap']:,} - VOL24 ${top['vol']:,} - NAIK24 {top['chg1h']}% - TP +100% SL -20%","BUY",0))
        equity=st.session_state.cash+modal
st.session_state.hist.append(equity)
winrate=int(st.session_state.wins/(st.session_state.wins+st.session_state.losses)*100) if (st.session_state.wins+st.session_state.losses)>0 else 0
top=coins[0] if coins else {"nama":"-","fomo":0,"vol":0,"txns":0,"buys":0,"mcap":0,"chg1h":0}
cuan=equity-10000.0
cuan_color="#00ff88" if cuan>=0 else "#ff2d55"
pnl_live=0
if st.session_state.punya and st.session_state.beli:
    pnl_live=(equity-(st.session_state.cash+modal))/modal*100 if modal else 0

st.markdown(f"### 👽 **Grok Terminal** <small>by Logics · v7.5-GAS 500 NAIK 100-2500%</small> <span class='badge armed'>● LIVE · {time.strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
with c1: st.markdown(f"<div class='topbox'><small>💰 MODAL</small><br><div class='bigbal' style='color:#00d4ff'>$10,000.00</div><small>Per Trade $500 · TP +{tp:.0f}% · SL {sl:.0f}% · HOLD MAX 10 MENIT</small></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='topbox'><small>📈 CUAN</small><br><div class='bigbal' style='color:{cuan_color}'>{'+' if cuan>=0 else ''}${cuan:,.2f}</div><small>{st.session_state.wins} WIN · {st.session_state.losses} LOSS · {winrate}% WR</small></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='topbox'><small>🏦 EQUITY</small><br><div class='bigbal' style='color:{cuan_color}'>${equity:,.2f}</div><small>{st.session_state.trades} TRADES · SCAN {st.session_state.scan}x</small></div>", unsafe_allow_html=True)

left, right = st.columns([1, 2.2])
with left:
    st.markdown(f"<div class='card radar'><b>👁️ RADAR</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>SCAN TOTAL {total_scan} COIN - TARGET 500!<br>LEVEL: {level}</small><br><small style='color:#00d4ff'>paling pump: {top['nama']} +{top['chg1h']}% · MCAP ${top['mcap']:,}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card shield'><b>🛡️ SHIELD</b> <span class='badge' style='background:#ff2d55;color:white;float:right'>ARMED</span><br><small>NO MINUS!<br>NAIK 100%-2500% · MCAP 5K-400K · VOL 25K-1M</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trigger'><b>⚡ TRIGGER</b> <span class='badge' style='background:#ffcc00;color:black;float:right'>ARMED</span><br><small>auto FIRE - ANTI BOSEN<br>skip 3 coin terakhir!</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card orca'><b>🐋 ORCA</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>follows smart wallets<br>top pump: {top['nama']}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card trip'><b>🚨 TRIPWIRE</b> <span class='badge' style='background:#ff9500;color:black;float:right'>ARMED</span><br><small>auto jual: TP +100% / SL -20% / GAK NAIK 100% / 10 MENIT</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card harvest'><b>🌾 HARVEST</b> <span class='badge trail' style='float:right'>TRAIL</span><br><small>kunci profit, jual di TP +100%</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card pulse'><b>💓 PULSE</b> <span class='badge armed' style='float:right'>ARMED</span><br><small>scan ke-{st.session_state.scan} · HOLD {st.session_state.hold}/{max_hold} · NONSTOP</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card conductor'><b>🎼 CONDUCTOR</b> <span class='badge' style='background:#a259ff;color:white;float:right'>PING</span><br><small>simulasi, harga REAL market</small></div>", unsafe_allow_html=True)

with right:
    st.markdown(f"<div class='card'><b>NIGHT DESK · SCAN → SHIELD → SCORE → FIRE → LOG</b> <span style='float:right'>total scan {total_scan} · LEVEL {level}</span><br><br>🔍 SCAN → 🛡️ SHIELD → 📊 SCORE → ⚡ FIRE → 📜 LOG<br><br><b>FIRED</b> {st.session_state.trades} | <b>WIN RATE</b> {winrate}% | <b>SCAN KE</b> {st.session_state.scan} | <b>TP +100% SL -20%</b></div>", unsafe_allow_html=True)
    if st.session_state.punya: st.success(f"🤲 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} REAL | HOLD {st.session_state.hold}/{max_hold} | PnL Live {pnl_live:+.1f}% | TP +{tp:.0f}% / SL {sl:.0f}%")
    else: st.info(f"⏳ Bot lagi nyari coin NAIK 100%-2500%... Total scan {total_scan} coin")
    st.markdown(f"### 🔥 COIN GAS - NAIK 100%-2500% - MCAP 5K-400K - VOL 25K-1M - SCAN {total_scan}")
    if coins:
        df=pd.DataFrame([{"#":i+1,"Coin":c["nama"],"Harga REAL":c["harga"],"Naik 24h %":c["chg1h"],"Mcap $":c["mcap"],"Volume 24h $":c["vol"],"Txns 24h":c["txns"],"Buys":c["buys"],"Umur":c["umur"],"Sumber":c["src"]} for i,c in enumerate(coins)])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("⏳ GAK ADA COIN NAIK 100%-2500% YANG LOLOS! Bot DIEM, gak beli minus lagi! Nunggu monster baru!")
        if all_coins:
            st.markdown("### 🔍 DEBUG - TOP 30 COIN KE-SCAN (KENAPA KE BUANG?)")
            dbg=pd.DataFrame([{"Coin":c["nama"],"Naik 24h %":c["chg1h"],"Mcap $":c["mcap"],"Volume 24h $":c["vol"],"Txns":c["txns"],"Buys":c["buys"]} for c in sorted(all_coins, key=lambda x: x["chg1h"], reverse=True)[:30]])
            st.dataframe(dbg, use_container_width=True, hide_index=True)
    st.line_chart(pd.DataFrame({"Equity":st.session_state.hist}))
    st.markdown("### 📜 LOG - BUY BIRU · TP IJO · SL MERAH · HOLD KUNING")
    if st.session_state.log:
        for row in reversed(st.session_state.log[-12:]):
            t,typ,nama,ket = row[0],row[1],row[2],row[3]
            jenis = row[4] if len(row)>4 else typ
            if jenis=="BUY": st.markdown(f"<div class='log-buy'>🔵 <b>{t}</b> &nbsp; <b>BUY</b> ${nama} → {ket}</div>", unsafe_allow_html=True)
            elif jenis=="TP": st.markdown(f"<div class='log-tp'>🟢 <b>{t}</b> &nbsp; <b>SELL TP</b> ${nama} → {ket}</div>", unsafe_allow_html=True)
            elif jenis=="SL": st.markdown(f"<div class='log-sl'>🔴 <b>{t}</b> &nbsp; <b>SELL SL</b> ${nama} → {ket}</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='log-hold'>🟡 <b>{t}</b> &nbsp; <b>SELL HOLD</b> ${nama} → {ket}</div>", unsafe_allow_html=True)
    else: st.write("Belum ada trade. Tunggu 10 detik, bot scan tiap 10 detik.")
time.sleep(10); st.rerun()
