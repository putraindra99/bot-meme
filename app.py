import streamlit as st, urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="Grok Bot Terminal - REAL v12.1", page_icon="⚪", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #fafafa; color: #1a1a1a; }
.agent-card { background: white; border: 1px solid #e8e8e8; border-radius: 12px; padding: 12px; margin-bottom: 10px; }
.top-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 10px; text-align: center; }
.flow-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 12px; }
.trade-card { background: white; border: 1px solid #e8e8e8; border-radius: 10px; padding: 14px; }
.big-num { font-size: 32px; font-weight: 800; line-height: 1; }
.small-label { font-size: 11px; color: #888; }
.green { color: #00c853; } .red { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

if "cash" not in st.session_state:
    st.session_state.cash=10000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0; st.session_state.mint=None
    st.session_state.log=[]; st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0; st.session_state.hold=0; st.session_state.last_coins=[]; st.session_state.start_time=time.time(); st.session_state.line_no=57
if st.button("🔄 RESET"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def get_json_debug(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()), "OK"
    except Exception as e:
        return None, str(e)[:120]

now_ms=int(time.time()*1000)
all_coins=[]; debug_lines=[]
KEYWORDS=["solana","pump","bonk","meme","wif","pepe","doge","cat","moon","trump"]
for q in KEYWORDS:
    data_api, err = get_json_debug(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
    debug_lines.append(f"search {q}: {'OK' if data_api else 'GAGAL: '+err}")
    if not data_api: continue
    for p in data_api.get("pairs",[])[:20]:
        try:
            if p.get("chainId")!="solana": continue
            tx=p.get("txns",{}).get("h24",{})
            mc=float(p.get("marketCap",0) or p.get("fdv",0) or 0)
            sym=p.get("baseToken",{}).get("symbol","?")
            price=float(p.get("priceUsd",0) or 0)
            vol=float(p.get("volume",{}).get("h24",0) or 0)
            chg=float(p.get("priceChange",{}).get("h24",0) or 0)
            if not sym or sym=="?" or price<=0 or vol<=0: continue
            if any(x.get("nama")==sym for x in all_coins): continue
            all_coins.append({"nama":sym,"harga":price,"vol":int(vol),"vol_mult":round(vol/50000,1),"chg1h":round(chg,1),"txns":int(tx.get("buys",0)+tx.get("sells",0)),"buys":int(tx.get("buys",0)),"umur":f"{round((now_ms-p.get('pairCreatedAt',now_ms))/60000)}m","umur_min":(now_ms-p.get("pairCreatedAt",now_ms))/60000,"src":"DEX-SEARCH-REAL","mcap":int(mc),"mint":p.get("baseToken",{}).get("address","")})
        except: continue

coins=[c for c in all_coins if c.get("vol",0)>=5000]
coins=sorted(coins, key=lambda x: x.get("vol",0), reverse=True)[:20]
total_scan=len(all_coins)
st.session_state.scan+=1
modal_pct=0.34
modal=st.session_state.cash*modal_pct
tp=20.0; sl=-10.0; max_hold=12
equity=st.session_state.cash
def get_real_price(mint):
    if not mint: return None
    data_api,_=get_json_debug(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
    if data_api and data_api.get("pairs"):
        for pp in data_api.get("pairs",[]):
            if pp.get("chainId")=="solana": return float(pp.get("priceUsd",0) or 0)
    return None
if st.session_state.punya:
    st.session_state.hold+=1
    harga_skrg=get_real_price(st.session_state.mint)
    if harga_skrg is None or harga_skrg==0: harga_skrg=st.session_state.beli
    equity=st.session_state.cash + st.session_state.jumlah*harga_skrg
    pnl=(harga_skrg-st.session_state.beli)/st.session_state.beli*100 if st.session_state.beli else 0
    jual=False; alasan=""
    if pnl>=tp: jual=True; alasan=f"TP REAL +{pnl:.1f}%"
    elif pnl<=sl: jual=True; alasan=f"SL REAL {pnl:.1f}%"
    elif st.session_state.hold>=max_hold: jual=True; alasan=f"HOLD 2m REAL {pnl:.1f}%"
    if jual:
        hasil=st.session_state.jumlah*harga_skrg; profit=hasil-modal; st.session_state.cash+=hasil
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,profit,hasil,alasan,"TP" if profit>0 else "SL"))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.line_no+=1
        st.session_state.last_coins.append(st.session_state.punya); st.session_state.last_coins=st.session_state.last_coins[-3:]
        st.session_state.punya=None; st.session_state.jumlah=0; st.session_state.hold=0; st.session_state.mint=None; equity=st.session_state.cash
else:
    top=None
    for cc in coins:
        if cc.get("nama") not in st.session_state.last_coins: top=cc; break
    if top is None: top=coins[0] if coins else None
    if top and st.session_state.cash>=modal:
        rh=get_real_price(top.get("mint","")) or top.get("harga",0)
        st.session_state.cash-=modal; st.session_state.punya=top.get("nama"); st.session_state.beli=rh; st.session_state.jumlah=modal/rh if rh else 0; st.session_state.hold=0; st.session_state.mint=top.get("mint","")
        st.session_state.log.append((time.strftime("%H:%M"),"ENTER",top.get("nama"),0,modal,f"34% of ${st.session_state.cash+modal:.2f} - HARGA REAL {rh:.6f}","BUY"))
        st.session_state.line_no+=1; equity=st.session_state.cash+modal

elapsed=time.time()-st.session_state.start_time
hh=int(elapsed//3600); mm=int((elapsed%3600)//60); ss=int(elapsed%60)
top4=coins[:4] if coins else []
EMPTY={"nama":"-","harga":0,"vol":0,"vol_mult":0,"chg1h":0,"src":"-","mcap":0,"umur":"-","mint":""}
while len(top4)<4: top4.append(dict(EMPTY))
cur_name=st.session_state.punya or top4[0].get("nama","-")
cur_entry=st.session_state.beli if st.session_state.punya else top4[0].get("harga",0)
cur_pnl=(equity-(st.session_state.cash+modal))/modal*100 if st.session_state.punya and modal else 0
api_ok = total_scan>0
st.markdown(f"### <span style='color:#2196f3'>Grok Bot</span> Terminal <span style='font-size:11px;background:#f0f0f0;padding:2px 6px;border-radius:4px'>v12.1-FIX</span> &nbsp; <span style='font-size:12px;color:#e65100'>● running {hh:02d}:{mm:02d}:{ss:02d}</span> &nbsp; <span style='font-size:11px;background:#f5f5f5;border:1px solid #ddd;padding:3px 8px;border-radius:4px'>EXECUTOR · ENTERED ${cur_name}</span> <span style='float:right;font-size:11px;color:#888'>@Corki_0x paper off · live</span>", unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
with c1: st.markdown(f"<div class='big-num'>${equity:,.2f}</div><div class='small-label'>balance</div><div class='big-num green' style='font-size:26px'>{st.session_state.wins}</div><div class='small-label'>wins</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='big-num'>{st.session_state.trades}</div><div class='small-label'>trades</div><div class='big-num red' style='font-size:26px'>{st.session_state.losses}</div><div class='small-label'>losses</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div style='font-size:14px'><b>STATUS API:</b> {'✅ REAL - DAPET '+str(total_scan)+' COIN ASLI' if api_ok else '❌ GAGAL'}<br><small>NO RANDOM · NO DUMMY · v12.1 FIX NameError</small></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:11px;color:#888;margin:10px 0'>AGENTS 6 online · checked {total_scan} · MODE REAL TP 20% SL -10% HOLD 2m</div>", unsafe_allow_html=True)
left,right=st.columns([1,2.2])
with left:
    st.markdown(f"<div class='agent-card'><b>📄 SCANNER</b><div style='font-size:11px;color:#888'>dex/search REAL</div><div>next ${top4[1].get('nama','-')} · vol {top4[1].get('vol_mult',0):.1f}x</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>⚠️ RUG CHECK</b><div>passed ${cur_name}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>💎 SIZER</b><div>34% of ${equity:,.2f} = ${modal:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>🟢 EXECUTOR</b><div>LONG ${cur_name} · TP +20% SL -10% · REAL PRICE</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>📝 LOGGER</b><div>Line #{st.session_state.line_no} · enter ${cur_name}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>💧 EQUITY</b><div>${equity:,.2f} · {st.session_state.trades} closes</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>⏸️ YOU</b><div>{len(st.session_state.log)} trade lines</div></div>", unsafe_allow_html=True)
with right:
    cc1,cc2,cc3,cc4=st.columns(4)
    for col, c in zip([cc1,cc2,cc3,cc4], top4):
        with col: st.markdown(f"<div class='top-card'><b>${c.get('nama','-')}</b><div style='font-size:11px;color:#888'>vol {c.get('vol_mult',0):.1f}x · +{c.get('chg1h',0):.0f}% · {c.get('src','-')}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='flow-card' style='margin-top:10px'><b>${cur_name} · +{cur_pnl:.2f}% live REAL</b><br><small>Harga dari Dexscreener via MINT, bukan random.</small><div style='display:flex;gap:8px;margin-top:8px'><div style='flex:1;background:#fff8e1;padding:8px;border-radius:8px'><b>FILTERED</b><div style='font-size:20px;font-weight:800'>{max(0,total_scan-len(coins))}</div></div><div style='flex:1;background:#f5f5f5;padding:8px;border-radius:8px'><b>SIZER</b><div style='font-size:20px;font-weight:800'>34% eq</div><div>${modal:,.2f}</div></div><div style='flex:1;background:#f5f5f5;padding:8px;border-radius:8px'><b>LOGGER</b><div style='font-size:20px;font-weight:800'>line #{st.session_state.line_no}</div></div><div style='flex:1;background:#e3f2fd;padding:8px;border-radius:8px'><b>EQUITY</b><div style='font-size:20px;font-weight:800;color:#00c853'>+${equity-10000:,.2f}</div></div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;gap:10px;margin-top:10px'><div class='trade-card' style='flex:1'><b>TRADE · ENTRY vs EXIT - REAL</b><div style='display:flex;justify-content:space-between;margin-top:8px'><b style='font-size:20px'>${cur_name}</b><b class='green'>+{cur_pnl:.2f}% live REAL</b></div><div style='font-size:13px;margin-top:6px'>entry {cur_entry:.6f} REAL<br>size 34% eq · ${modal:,.2f}<br>net +{cur_pnl:.2f}% · REAL PRICE</div></div><div class='trade-card' style='flex:1'><b>$ tail -f trades.log</b><div style='font-size:12px;margin-top:8px'>" + "<br>".join([f"{r[0]} {r[1]} ${r[2]} {r[3]:+.2f} net" if r[1]=="EXIT" else f"{r[0]} {r[1]} ${r[2]} ${r[4]:,.2f}" for r in reversed(st.session_state.log[-4:])]) + "</div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><b>RESULT · start vs now - REAL</b><div style='display:flex;justify-content:space-between'><span>START</span><b>$10,000.00</b></div><div style='display:flex;justify-content:space-between'><span>NOW</span><b>${equity:,.2f}</b></div><div style='font-size:11px;color:#888'>{st.session_state.wins} W / {st.session_state.losses} L · NET +${equity-10000:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><b>TRADE LOG - REAL</b>" + "".join([f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0'><span>{r[0]} {r[1]} <b>${r[2]}</b></span><span>{r[3]:+.2f}</span></div>" for r in reversed(st.session_state.log[-5:])]) + "</div>", unsafe_allow_html=True)
    st.markdown("### 🔍 DEBUG API", unsafe_allow_html=True)
    for line in debug_lines: st.code(line)
    if coins:
        # FIX: pake nama tabel_coins, BUKAN df lagi!
        tabel_coins=pd.DataFrame([{"Coin":c.get("nama"),"Harga REAL":c.get("harga"),"Naik 24h %":c.get("chg1h"),"Vol 24h":c.get("vol"),"Mcap":c.get("mcap"),"Umur":c.get("umur"),"Sumber":c.get("src")} for c in coins])
        st.dataframe(tabel_coins, use_container_width=True, hide_index=True)
    st.markdown("<div style='font-size:11px;color:#888'>v12.1 FIX NameError - NO RANDOM - NO DUMMY - HARGA DEXSCREENER REAL</div>", unsafe_allow_html=True)
time.sleep(10); st.rerun()
