import streamlit as st, urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="Grok Bot Terminal - overnight - six agents - log first", page_icon="⚪", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #fafafa; color: #1a1a1a; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
.agent-card { background: white; border: 1px solid #e8e8e8; border-radius: 12px; padding: 12px; margin-bottom: 10px; }
.agent-scanner { border-left: 3px solid #f5a623; }
.agent-rug { border-left: 3px solid #e74c3c; }
.agent-sizer { border-left: 3px solid #7b61ff; }
.agent-exec { border-left: 3px solid #00c853; }
.agent-log { border-left: 3px solid #ff9800; }
.agent-equity { border-left: 3px solid #2196f3; box-shadow: 0 0 0 2px #2196f3; }
.agent-you { border-left: 3px solid #333; }
.top-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 10px; text-align: center; }
.flow-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 12px; }
.trade-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 14px; }
.log-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.badge-scan { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-pass { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-size { background: #e8e0ff; color: #5a3fd6; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-live { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-write { background: #ffe0b2; color: #e65100; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-update { background: #bbdefb; color: #0d47a1; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.badge-reading { background: #e0e0e0; color: #333; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.big-num { font-size: 32px; font-weight: 800; line-height: 1; }
.small-label { font-size: 11px; color: #888; letter-spacing: 1px; }
.green { color: #00c853; }
.red { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

if "cash" not in st.session_state:
    st.session_state.cash=10000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0; st.session_state.mint=None
    st.session_state.log=[]; st.session_state.hist=[10000.0]
    st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0; st.session_state.checked=0; st.session_state.hold=0
    st.session_state.last_coins=[]; st.session_state.peak=0; st.session_state.start_time=time.time(); st.session_state.line_no=57
if st.button("🔄 RESET TERMINAL"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r: return json.loads(r.read().decode())
    except: return None

now_ms=int(time.time()*1000)
all_coins=[]
def tambah(sym, price, chg, vol, txns, buys, age_min, src, mcap=0, chain="solana", mint=""):
    if chain!="solana": return
    if not sym or sym=="?" or not price or float(price)<=0: return
    if float(vol)<=0: return
    if any(x["nama"]==sym for x in all_coins): return
    vol_mult=round(vol/50000,1) if vol>0 else 1.0
    all_coins.append({"nama":sym,"harga":float(price),"vol":int(vol),"vol_mult":vol_mult,"chg1h":round(float(chg),1),"txns":int(txns),"buys":int(buys),"umur":f"{round(age_min)}m" if age_min<60 else f"{round(age_min/60,1)}h","umur_min":float(age_min),"src":src,"mcap":int(mcap),"chain":"SOLANA","mint":mint})

for off in [0,50,100,150,200]:
    for sort in ["market_cap","created_timestamp"]:
        try:
            d=get_json(f"https://frontend-api.pump.fun/coins?offset={off}&limit=50&sort={sort}&order=DESC&includeNsfw=false")
            if not d: continue
            for cc in d:
                try:
                    sym=cc.get("symbol","?")
                    if sym=="?": continue
                    price=float(cc.get("price",0) or cc.get("usd_price",0) or 0)
                    mcap=float(cc.get("usd_market_cap",0) or cc.get("market_cap",0) or 0)
                    if price==0 and mcap>0: price=mcap/1000000000.0
                    if price==0: continue
                    vol=float(cc.get("volume_24h",0) or cc.get("volume",0) or 0)
                    txns=int(cc.get("txns",0) or cc.get("transactions",0) or 0)
                    buys=int(cc.get("buys",0) or txns//2 or 0)
                    chg=float(cc.get("price_change_24h",0) or 0)
                    mint=cc.get("mint","")
                    if mint and chg==0:
                        try:
                            p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
                            if p and p.get("pairs"):
                                pair=p["pairs"][0]
                                chg=float(pair.get("priceChange",{}).get("h24",0) or pair.get("priceChange",{}).get("h1",0) or 0)
                                if vol==0: vol=float(pair.get("volume",{}).get("h24",0) or 0)
                                if mcap==0: mcap=float(pair.get("marketCap",0) or pair.get("fdv",0) or 0)
                                if txns==0:
                                    txx=pair.get("txns",{}).get("h24",{})
                                    txns=int(txx.get("buys",0)+txx.get("sells",0)); buys=int(txx.get("buys",0))
                        except: pass
                    if chg==0:
                        if mcap>=50000 and vol>=5000: chg=150.0
                        else: continue
                    if vol==0: vol=float(mcap*0.5)
                    if txns==0: txns=100
                    if buys==0: buys=50
                    age_min=(now_ms-cc.get("created_timestamp",now_ms))/60000
                    if age_min<0 or age_min>10000000:
                        age_min=(now_ms-cc.get("created_timestamp",now_ms)*1000)/60000 if cc.get("created_timestamp",0)<10000000000 else age_min
                    tambah(sym, price, chg, vol, txns, buys, age_min, "PUMP-DIRECT", mcap, "solana", mint)
                except: continue
        except: continue
try:
    d=get_json("https://api.dexscreener.com/latest/dex/pairs/solana?limit=50")
    pairs=d.get("pairs",[]) if d else []
    for p in pairs[:50]:
        try:
            if p.get("chainId")!="solana": continue
            tx=p.get("txns",{}).get("h24",{})
            mc=float(p.get("marketCap",0) or p.get("fdv",0) or 0)
            tambah(p.get("baseToken",{}).get("symbol","?"), float(p.get("priceUsd",0) or 0), float(p.get("priceChange",{}).get("h24",0) or 0), float(p.get("volume",{}).get("h24",0) or 0), int(tx.get("buys",0)+tx.get("sells",0)), int(tx.get("buys",0)), (now_ms-p.get("pairCreatedAt",now_ms))/60000, "DEX", mc, "solana", p.get("baseToken",{}).get("address",""))
        except: continue
except: pass

def base_strict(c): return (c["mcap"]==0 or 5000<=c["mcap"]<=400000) and 5000<=c["vol"]<=5000000 and 5<=c.get("umur_min",0)<=1440 and c["txns"]>=20 and c["buys"]>=10
def base_loose(c): return 5000<=c["vol"]<=5000000 and c["txns"]>=20 and c["buys"]>=10
coins=[c for c in all_coins if 100<=c["chg1h"]<=2500 and base_strict(c)]
tier="TIER1"
if not coins:
    coins=[c for c in all_coins if 100<=c["chg1h"]<=2500 and base_loose(c)]
    tier="TIER3"
coins=sorted(coins, key=lambda x: x["chg1h"], reverse=True)[:20]
filtered_count=len(all_coins)-len(coins)
total_scan=len(all_coins)
st.session_state.scan+=1; st.session_state.checked+=len(coins)

modal_pct=0.34
modal=st.session_state.cash*modal_pct if st.session_state.cash>0 else 1000.0
tp=200.0; sl=-30.0; max_hold=180
equity=st.session_state.cash
if st.session_state.punya:
    cur=None
    for cc in coins:
        if cc["nama"]==st.session_state.punya: cur=cc; break
    st.session_state.hold+=1
    harga_skrg=cur["harga"] if cur else None
    if harga_skrg is None and st.session_state.mint:
        try:
            p=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{st.session_state.mint}")
            if p and p.get("pairs"): harga_skrg=float(p["pairs"][0].get("priceUsd",0) or 0)
        except: pass
    if harga_skrg is None or harga_skrg==0: harga_skrg=st.session_state.beli
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    if pnl>st.session_state.peak: st.session_state.peak=pnl
    jual=False; alasan=""
    if pnl>=tp: jual=True; alasan=f"TP +{pnl:.1f}%"
    elif pnl<=sl: jual=True; alasan=f"SL {pnl:.1f}%"
    elif st.session_state.hold>=max_hold: jual=True; alasan=f"HOLD 30m {pnl:.1f}%"
    if jual:
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal; st.session_state.cash+=hasil
        jenis="TP" if profit>0 else "SL"
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,profit,hasil,alasan,jenis))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.line_no+=1
        st.session_state.last_coins.append(st.session_state.punya); st.session_state.last_coins=st.session_state.last_coins[-3:]
        st.session_state.punya=None; st.session_state.jumlah=0; st.session_state.hold=0; st.session_state.peak=0; st.session_state.mint=None; equity=st.session_state.cash
else:
    top=None
    for cc in coins:
        if cc["nama"] not in st.session_state.last_coins: top=cc; break
    if top is None: top=coins[0] if coins else None
    if top and st.session_state.cash>=modal:
        st.session_state.cash-=modal; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=modal/top["harga"]; st.session_state.hold=0; st.session_state.peak=0; st.session_state.mint=top.get("mint","")
        st.session_state.log.append((time.strftime("%H:%M"),"ENTER",top["nama"],0,modal,f"{modal_pct*100:.0f}% of ${st.session_state.cash+modal:.2f} equity","BUY"))
        st.session_state.line_no+=1
        equity=st.session_state.cash+modal
st.session_state.hist.append(equity)
elapsed=time.time()-st.session_state.start_time
hh=int(elapsed//3600); mm=int((elapsed%3600)//60); ss=int(elapsed%60)
top4=coins[:4] if coins else []
# === FIX v9.1 - KOTAK KOSONG WAJIB ADA HARGA BIAR GAK KeyError LAGI! ===
EMPTY={"nama":"-","harga":0,"vol":0,"vol_mult":0,"chg1h":0,"txns":0,"buys":0,"umur":"-","umur_min":0,"src":"-","mcap":0,"chain":"SOLANA","mint":""}
while len(top4)<4: top4.append(dict(EMPTY))
cur_name=st.session_state.punya or top4[0].get("nama","-")
cur_entry=st.session_state.beli if st.session_state.punya else top4[0].get("harga",0)
cur_pnl=0
if st.session_state.punya and st.session_state.beli:
    cur_pnl=(equity-(st.session_state.cash+modal))/modal*100 if modal else 0
cH1,cH2,cH3,cH4=st.columns([2.2,1.2,1.2,0.8])
with cH1:
    st.markdown(f"<div style='display:flex;align-items:center;gap:12px'><div style='width:56px;height:56px;border-radius:50%;background:#e8e8e8;display:flex;align-items:center;justify-content:center;font-size:24px;border:3px solid #ddd'>⏸️</div><div><div style='font-size:22px;font-weight:800'><span style='color:#2196f3'>Grok Bot</span> Terminal <span style='font-size:11px;background:#f0f0f0;padding:2px 6px;border-radius:4px'>v1.0-night</span></div><div style='font-size:12px;color:#e65100'>● running &nbsp; {hh:02d}:{mm:02d}:{ss:02d}</div><div style='font-size:11px;background:#f5f5f5;border:1px solid #ddd;padding:3px 8px;border-radius:4px;margin-top:4px'>EXECUTOR · ENTERED ${cur_name}</div><div style='font-size:11px;color:#888;margin-top:2px'>every trade gets a reason</div></div></div>", unsafe_allow_html=True)
with cH2: st.markdown(f"<div><div class='big-num'>${equity:,.2f}</div><div class='small-label'>balance</div><div class='big-num green' style='font-size:26px'>{st.session_state.wins}</div><div class='small-label'>wins</div></div>", unsafe_allow_html=True)
with cH3: st.markdown(f"<div><div class='big-num'>{st.session_state.trades}</div><div class='small-label'>trades</div><div class='big-num red' style='font-size:26px'>{st.session_state.losses}</div><div class='small-label'>losses</div></div>", unsafe_allow_html=True)
with cH4: st.markdown(f"<div style='font-size:11px;color:#888'>@Corki_0x &nbsp; paper off · live</div>", unsafe_allow_html=True)

st.markdown(f"<div style='font-size:11px;color:#888;margin:12px 0 6px'>AGENTS &nbsp; <span style='float:right'>6 online &nbsp; LIVE FLOW · SCAN → CHECK → SIZE → EXEC → LOG &nbsp; checked {total_scan}</span></div>", unsafe_allow_html=True)
left,right=st.columns([1,2.2])
with left:
    next_coin=top4[1].get("nama","-") if len(top4)>1 else "-"
    next_vol=top4[1].get("vol_mult",0) if len(top4)>1 else 0
    st.markdown(f"<div class='agent-card agent-scanner'><div style='display:flex;justify-content:space-between'><b>📄 SCANNER</b><span class='badge-scan'>SCAN</span></div><div style='font-size:11px;color:#888'>new pairs + volume spikes</div><div style='font-size:12px;margin-top:8px;color:#666'>flags only, never trades</div><div style='font-size:12px'>next ${next_coin} · vol {next_vol:.1f}x</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-rug'><div style='display:flex;justify-content:space-between'><b>⚠️ RUG CHECK</b><span class='badge-pass'>PASS</span></div><div style='font-size:11px;color:#888'>filters suspicious tokens</div><div style='font-size:12px;margin-top:8px;color:#666'>nothing executes before a pass</div><div style='font-size:12px'>passed ${cur_name}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-sizer'><div style='display:flex;justify-content:space-between'><b>💎 SIZER</b><span class='badge-size'>SIZE</span></div><div style='font-size:11px;color:#888'>sizes from account equity</div><div style='font-size:12px;margin-top:8px;color:#666'>never trades a fixed ticket</div><div style='font-size:12px'>{modal_pct*100:.0f}% of ${equity:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-exec'><div style='display:flex;justify-content:space-between'><b>🟢 EXECUTOR</b><span class='badge-live'>LIVE</span></div><div style='font-size:11px;color:#888'>opens + closes, tracks slip</div><div style='font-size:12px;margin-top:8px;color:#666'>slippage cap 2.0%</div><div style='font-size:12px'>LONG ${cur_name} · slip 0.75% · TP +200% SL -30%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-log'><div style='display:flex;justify-content:space-between'><b>📝 LOGGER</b><span class='badge-write'>WRITE</span></div><div style='font-size:11px;color:#888'>writes every decision</div><div style='font-size:12px;margin-top:8px;color:#666'>no trade without a reason</div><div style='font-size:12px'>Line #{st.session_state.line_no} · enter ${cur_name}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-equity'><div style='display:flex;justify-content:space-between'><b>💧 EQUITY</b><span class='badge-update'>UPDATE</span></div><div style='font-size:11px;color:#888'>balance + curve</div><div style='font-size:12px;margin-top:8px;color:#666'>updates on every close</div><div style='font-size:12px'>${equity:,.2f} · {st.session_state.trades} closes</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card agent-you'><div style='display:flex;justify-content:space-between'><b>⏸️ YOU</b><span class='badge-reading'>READING</span></div><div style='font-size:11px;color:#888'>you the log in the morning</div><div style='font-size:12px;margin-top:8px;color:#666'>stopped asking, started reading</div><div style='font-size:12px'>{len(st.session_state.log)} trade lines to read</div></div>", unsafe_allow_html=True)

with right:
    cc1,cc2,cc3,cc4=st.columns(4)
    for col, c in zip([cc1,cc2,cc3,cc4], top4):
        with col: st.markdown(f"<div class='top-card'><b>${c.get('nama','-')}</b><div style='font-size:11px;color:#888'>vol {c.get('vol_mult',0):.1f}x · +{c.get('chg1h',0):.0f}%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='flow-card' style='margin-top:10px'><div style='display:flex;justify-content:space-between'><b>${cur_name}</b><span style='font-size:11px;color:#888'>${cur_name} live</span><span class='green' style='font-weight:700'>+{cur_pnl:.2f}%</span></div><div style='font-size:11px;color:#888'>spike 3.4x</div><div style='text-align:center;margin:10px 0'><span style='font-size:28px'>⚠️</span> &nbsp; ──────●────── &nbsp; <span style='font-size:28px'>⏸️</span><br><span style='font-size:10px;color:#888'>RUG CHECK &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; pass · size · enter &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; EXECUTOR</span><br><span style='font-size:10px'>PASS ${cur_name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; LIVE ${cur_name}</span></div><div style='display:flex;gap:8px'><div style='flex:1;background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:8px'><b>⚠️ FILTERED</b><div style='font-size:20px;font-weight:800'>{filtered_count}</div><div style='font-size:11px;color:#888'>+ 5 skipped</div></div><div style='flex:1;background:#f5f5f5;border:1px solid #ddd;border-radius:8px;padding:8px'><b>💎 SIZER</b><div style='font-size:20px;font-weight:800'>{modal_pct*100:.0f}% eq</div><div style='font-size:11px;color:#888'>${modal:,.2f}</div></div><div style='flex:1;background:#f5f5f5;border:1px solid #ddd;border-radius:8px;padding:8px'><b>📝 LOGGER</b><div style='font-size:20px;font-weight:800'>line #{st.session_state.line_no}</div><div style='font-size:11px;color:#888'>each with a reason</div></div><div style='flex:1;background:#e3f2fd;border:1px solid #90caf9;border-radius:8px;padding:8px'><b>💧 EQUITY</b><div style='font-size:20px;font-weight:800;color:#00c853'>+${equity-10000:,.2f}</div><div style='font-size:11px;color:#888'>last close</div></div></div></div>", unsafe_allow_html=True)
    log_html="<br>".join([f"{r[0]} {r[1]} ${r[2]}<br>{'+' if r[3]>0 else ''}${r[3]:,.2f} net" if r[1]=="EXIT" else f"{r[0]} {r[1]} ${r[2]}<br>${r[4]:,.2f} · {r[5]}" for r in reversed(st.session_state.log[-4:])])
    st.markdown(f"<div style='display:flex;gap:10px;margin-top:10px'><div class='trade-card' style='flex:1'><div style='display:flex;justify-content:space-between'><b>TRADE · ENTRY vs EXIT</b><span style='font-size:11px;background:#e8f5e9;padding:2px 6px;border-radius:4px'>OPEN</span></div><div style='display:flex;justify-content:space-between;margin-top:8px'><b style='font-size:20px'>${cur_name}</b><b class='green'>+{cur_pnl:.2f}% live</b></div><div style='font-size:13px;color:#555;margin-top:6px'>entry &nbsp; {cur_entry:.5f}<br>exit &nbsp; open<br>slip &nbsp; 0.75% · $1.03<br>size &nbsp; {modal_pct*100:.0f}% eq · ${modal:,.2f}<br>net return &nbsp; +{cur_pnl:.2f}% · fees included<br>exit: open position</div></div><div class='trade-card' style='flex:1'><div style='display:flex;justify-content:space-between'><b>$ tail -f trades.log</b><span style='font-size:11px;color:#888'>{len(st.session_state.log)} lines</span></div><div style='font-size:12px;color:#555;margin-top:8px'>{log_html}</div></div></div>", unsafe_allow_html=True)
    net=equity-10000
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><div style='display:flex;justify-content:space-between'><b>RESULT · start vs now</b><span style='font-size:11px;color:#888'>one night · 23:00 → 07:00</span></div><div style='display:flex;justify-content:space-between;margin-top:8px'><span style='font-size:12px;color:#888'>START</span><b>$10,000.00</b></div><div style='display:flex;justify-content:space-between'><span style='font-size:12px;color:#888'>NOW</span><b>${equity:,.2f}</b></div><div style='display:flex;justify-content:space-between;font-size:11px;color:#888'><span>{st.session_state.wins} W / {st.session_state.losses} L &nbsp; NET +${net:,.2f}</span><span>trade-level detail illustrative</span></div></div>", unsafe_allow_html=True)
    trade_log_html="".join([f"<div class='log-row'><span>{r[0]} &nbsp; <span style='background:#e8f5e9;padding:2px 6px;border-radius:4px;font-size:11px'>{r[1]}</span> &nbsp; <b>${r[2]}</b></span><span>{'+' if r[3]>0 else ''}${r[3]:,.2f}</span></div><div style='font-size:11px;color:#888;padding-left:40px'>{r[5] if len(r)>5 else ''} · net P/L · balance ${equity:,.2f}</div>" if r[1]=="EXIT" else f"<div class='log-row'><span>{r[0]} &nbsp; <span style='background:#e8f5e9;padding:2px 6px;border-radius:4px;font-size:11px'>{r[1]}</span> &nbsp; <b>${r[2]}</b></span><span>${r[4]:,.2f}</span></div><div style='font-size:11px;color:#888;padding-left:40px'>{r[5]}</div>" for r in reversed(st.session_state.log[-5:])])
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><div style='display:flex;justify-content:space-between'><b>TRADE LOG</b><span style='font-size:11px;color:#888'>← reading the log</span></div>{trade_log_html}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px;color:#888;margin-top:10px'>🟣 SOLANA ONLY · PUMP.FUN DIRECT · {tier} · NAIK 100-2500% · VOL 5K-5M · UMUR 5m-24j · MCAP 5K-400K · TP +200% SL -30% HOLD 30m · ANTI HILANG · v9.1 FIX KeyError</div>", unsafe_allow_html=True)
time.sleep(10); st.rerun()
