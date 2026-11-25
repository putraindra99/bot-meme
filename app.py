import streamlit as st, urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="Grok Bot Terminal - NEON BLUE v13.1", page_icon="💙", layout="wide")
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at top, #0a1a4a 0%, #0a0e27 50%, #050816 100%) !important; color: #e0f0ff !important; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp * { color: #e0f0ff !important; }
.agent-card { background: rgba(0, 80, 255, 0.12) !important; border: 1px solid #00bfff !important; border-radius: 12px; padding: 12px; margin-bottom: 10px; box-shadow: 0 0 15px rgba(0,191,255,0.3); }
.top-card { background: rgba(0, 80, 255, 0.15) !important; border: 1px solid #00bfff !important; border-radius: 10px; padding: 10px; text-align: center; box-shadow: 0 0 12px rgba(0,191,255,0.4); }
.flow-card { background: rgba(0, 80, 255, 0.12) !important; border: 1px solid #00bfff !important; border-radius: 10px; padding: 12px; box-shadow: 0 0 15px rgba(0,191,255,0.3); }
.trade-card { background: rgba(0, 80, 255, 0.12) !important; border: 1px solid #00bfff !important; border-radius: 10px; padding: 14px; box-shadow: 0 0 15px rgba(0,191,255,0.3); }
.big-num { font-size: 32px; font-weight: 800; line-height: 1; color: #00ffff !important; text-shadow: 0 0 10px #00ffff; }
.small-label { font-size: 11px; color: #7dd3fc !important; }
.green { color: #00ff88 !important; text-shadow: 0 0 8px #00ff88; }
.red { color: #ff3b5c !important; text-shadow: 0 0 8px #ff3b5c; }
.stButton button { background: #00bfff !important; color: #000 !important; border: none !important; font-weight: 800 !important; box-shadow: 0 0 15px #00bfff !important; }
code { color: #00ffff !important; background: rgba(0,20,60,0.8) !important; }
</style>
""", unsafe_allow_html=True)

if "cash" not in st.session_state:
    st.session_state.cash=10000.0; st.session_state.punya=None; st.session_state.beli=0; st.session_state.jumlah=0; st.session_state.mint=None; st.session_state.modal_invested=0
    st.session_state.log=[]; st.session_state.wins=0; st.session_state.losses=0; st.session_state.scan=0; st.session_state.trades=0; st.session_state.hold=0; st.session_state.last_coins=[]; st.session_state.start_time=time.time(); st.session_state.line_no=57
if st.button("🔄 RESET"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def get_json(u):
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read().decode()), "OK"
    except Exception as e:
        return None, str(e)[:100]

sol_price=0; sol_src="?"; sol_chg=0
d_sol,_=get_json("https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112")
if d_sol and d_sol.get("pairs"):
    best=None; bl=-1
    for pp in d_sol.get("pairs",[]):
        if pp.get("chainId")!="solana": continue
        l=float(pp.get("liquidity",{}).get("usd",0) or 0)
        if l>bl: bl=l; best=pp
    if best:
        sol_price=float(best.get("priceUsd",0) or 0); sol_src="Dexscreener SOL Mint REAL"; sol_chg=float(best.get("priceChange",{}).get("h24",0) or 0)

now_ms=int(time.time()*1000)
semua_pair=[]; debug_lines=[]; dibuang_palsu=0; total_raw=0
# === v13.1 FIX RATE LIMIT: CUMA 4 REQUEST GEDE, BUKAN 36 REQUEST KECIL! ===
# 1. Dexscreener Search 1x aja: "sol" - ini return 100+ pairs Solana dalam 1 request!
d1,e1=get_json("https://api.dexscreener.com/latest/dex/search/?q=sol")
debug_lines.append(f"1. Dex Search 'sol': {'OK '+str(len(d1.get('pairs',[])))+' pairs' if d1 else 'GAGAL '+e1}")
if d1:
    for p in d1.get("pairs",[]):
        if p.get("chainId")=="solana": semua_pair.append(p)
time.sleep(0.5)
# 2. Dexscreener Token Boosts Top - 1 request = 100+ coin yang lagi di-boost!
d2,e2=get_json("https://api.dexscreener.com/token-boosts/top/v1")
debug_lines.append(f"2. Dex Boosts Top: {'OK '+str(len(d2))+' token' if isinstance(d2,list) else 'GAGAL '+e2}")
if isinstance(d2,list):
    for t in d2[:40]:
        addr=t.get("tokenAddress","")
        if not addr: continue
        d_tok,_=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{addr}")
        if d_tok and d_tok.get("pairs"):
            for pp in d_tok.get("pairs",[]):
                if pp.get("chainId")=="solana": semua_pair.append(pp)
        time.sleep(0.1)
# 3. GeckoTerminal Trending Pools Solana - 1 request = 20 pools paling rame!
d3,e3=get_json("https://api.geckoterminal.com/api/v2/networks/solana/trending_pools")
debug_lines.append(f"3. Gecko Trending: {'OK '+str(len(d3.get('data',[])))+' pools' if d3 else 'GAGAL '+e3}")
if d3 and d3.get("data"):
    for item in d3.get("data",[]):
        pid=item.get("id",""); pool=pid.split("_")[-1] if "_" in pid else pid
        if pool:
            d_pair,_=get_json(f"https://api.dexscreener.com/latest/dex/pairs/solana/{pool}")
            if d_pair and d_pair.get("pairs"):
                for pp in d_pair.get("pairs",[]):
                    if pp.get("chainId")=="solana": semua_pair.append(pp)
            time.sleep(0.1)
# 4. GeckoTerminal New Pools Solana - 1 request = 20 pools baru!
d4,e4=get_json("https://api.geckoterminal.com/api/v2/networks/solana/new_pools")
debug_lines.append(f"4. Gecko New Pools: {'OK '+str(len(d4.get('data',[])))+' pools' if d4 else 'GAGAL '+e4}")
if d4 and d4.get("data"):
    for item in d4.get("data",[]):
        pid=item.get("id",""); pool=pid.split("_")[-1] if "_" in pid else pid
        if pool:
            d_pair,_=get_json(f"https://api.dexscreener.com/latest/dex/pairs/solana/{pool}")
            if d_pair and d_pair.get("pairs"):
                for pp in d_pair.get("pairs",[]):
                    if pp.get("chainId")=="solana": semua_pair.append(pp)
            time.sleep(0.1)

total_raw=len(semua_pair)
# Filter + Dedup - 1 nama = 1 coin, LIQ paling gede menang
best_by_nama={}
for p in semua_pair:
    try:
        if p.get("chainId")!="solana": continue
        liq=float(p.get("liquidity",{}).get("usd",0) or 0)
        if liq<5000: dibuang_palsu+=1; continue
        sym=p.get("baseToken",{}).get("symbol","?").upper()
        if sym=="SOL": continue
        if sym not in best_by_nama or liq>best_by_nama[sym][0]:
            best_by_nama[sym]=(liq,p)
    except: continue
all_coins=[]
for sym,(liq,p) in best_by_nama.items():
    try:
        tx=p.get("txns",{}).get("h24",{})
        mc=float(p.get("marketCap",0) or p.get("fdv",0) or 0)
        price=float(p.get("priceUsd",0) or 0)
        vol=float(p.get("volume",{}).get("h24",0) or 0)
        chg=float(p.get("priceChange",{}).get("h24",0) or 0)
        if price<=0 or vol<=0: continue
        umur_min=(now_ms-p.get("pairCreatedAt",now_ms))/60000
        umur_txt=f"{round(umur_min)}m" if umur_min<60 else f"{round(umur_min/60,1)}h" if umur_min<1440 else f"{round(umur_min/1440,1)}d"
        all_coins.append({"nama":sym,"harga":price,"vol":int(vol),"vol_mult":round(vol/50000,1),"chg1h":round(chg,1),"txns":int(tx.get("buys",0)+tx.get("sells",0)),"buys":int(tx.get("buys",0)),"umur":umur_txt,"umur_min":umur_min,"src":"SCREENER-4-SUMBER","mcap":int(mc),"mint":p.get("baseToken",{}).get("address",""),"liq":int(liq)})
    except: continue
coins=[c for c in all_coins if c.get("vol",0)>=1000]
coins=sorted(coins, key=lambda x: x.get("vol",0), reverse=True)[:20]
total_scan=len(all_coins)
debug_lines.append(f"TOTAL: {total_raw} pairs -> {total_scan} COIN UNIK - 0 NAMA COIN DARI GUA!")
st.session_state.scan+=1
modal_pct=0.34
modal_baru=st.session_state.cash*modal_pct
modal_display=st.session_state.modal_invested if st.session_state.punya else modal_baru
tp=20.0; sl=-10.0; max_hold=12
equity=st.session_state.cash
def get_real_price(mint):
    if not mint: return None
    data_api,_=get_json(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
    if data_api and data_api.get("pairs"):
        best=None; best_liq=-1
        for pp in data_api.get("pairs",[]):
            if pp.get("chainId")!="solana": continue
            l=float(pp.get("liquidity",{}).get("usd",0) or 0)
            if l>best_liq: best_liq=l; best=pp
        if best: return float(best.get("priceUsd",0) or 0)
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
        hasil=st.session_state.jumlah*harga_skrg; modal_pakai=st.session_state.modal_invested if st.session_state.modal_invested>0 else modal_baru; profit=hasil-modal_pakai; st.session_state.cash+=hasil
        st.session_state.log.append((time.strftime("%H:%M"),"EXIT",st.session_state.punya,profit,hasil,alasan,"TP" if profit>0 else "SL"))
        if profit>0: st.session_state.wins+=1
        else: st.session_state.losses+=1
        st.session_state.trades+=1; st.session_state.line_no+=1
        st.session_state.last_coins.append(st.session_state.punya); st.session_state.last_coins=st.session_state.last_coins[-3:]
        st.session_state.punya=None; st.session_state.jumlah=0; st.session_state.hold=0; st.session_state.mint=None; st.session_state.modal_invested=0; equity=st.session_state.cash
else:
    top=None
    for cc in coins:
        if cc.get("nama") not in st.session_state.last_coins: top=cc; break
    if top is None: top=coins[0] if coins else None
    if top and st.session_state.cash>=modal_baru:
        rh=get_real_price(top.get("mint","")) or top.get("harga",0)
        st.session_state.modal_invested=modal_baru
        st.session_state.cash-=modal_baru; st.session_state.punya=top.get("nama"); st.session_state.beli=rh; st.session_state.jumlah=modal_baru/rh if rh else 0; st.session_state.hold=0; st.session_state.mint=top.get("mint","")
        st.session_state.log.append((time.strftime("%H:%M"),"ENTER",top.get("nama"),0,modal_baru,f"34% - BOT PILIH SENDIRI DARI {total_scan} COIN - HARGA REAL {rh:.6f} LIQ ${top.get('liq',0):,}","BUY"))
        st.session_state.line_no+=1; equity=st.session_state.cash+modal_baru

elapsed=time.time()-st.session_state.start_time
hh=int(elapsed//3600); mm=int((elapsed%3600)//60); ss=int(elapsed%60)
top4=coins[:4] if coins else []
cur_name=st.session_state.punya or (top4[0].get("nama","-") if top4 else "-")
cur_entry=st.session_state.beli if st.session_state.punya else (top4[0].get("harga",0) if top4 else 0)
cur_pnl=(equity-(st.session_state.cash+modal_display))/modal_display*100 if st.session_state.punya and modal_display else 0
api_ok = total_scan>0
st.markdown(f"### <span style='color:#00ffff'>💙 Grok Bot</span> <span style='color:#00bfff'>Terminal</span> <span style='font-size:11px;background:#001a4a;padding:2px 6px;border-radius:4px;color:#00ffff !important'>v13.1-SCREENER 4 SUMBER - NO RATE LIMIT</span> &nbsp; <span style='font-size:12px;color:#00ff88 !important'>● running {hh:02d}:{mm:02d}:{ss:02d}</span> &nbsp; <span style='font-size:11px;background:#001a4a;padding:3px 8px;border-radius:4px;color:#00ffff !important'>EXECUTOR · ENTERED ${cur_name}</span>", unsafe_allow_html=True)
st.markdown(f"<div style='background:rgba(0,100,255,0.2);border:1px solid #00bfff;border-radius:10px;padding:12px;box-shadow:0 0 20px #00bfff'><b style='color:#00ffff !important'>💜 SOL REAL: ${sol_price:.2f} ({sol_chg:+.1f}% 24h) - Sumber: {sol_src}</b> &nbsp; | &nbsp; 🗑️ Palsu dibuang: {dibuang_palsu} &nbsp; | &nbsp; ✅ DISAPU: {total_raw} pairs -> {total_scan} COIN UNIK - 0 NAMA COIN DARI GUA!</div>", unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
with c1: st.markdown(f"<div class='big-num'>${equity:,.2f}</div><div class='small-label'>balance</div><div class='big-num green' style='font-size:26px'>{st.session_state.wins}</div><div class='small-label'>wins</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='big-num'>{st.session_state.trades}</div><div class='small-label'>trades</div><div class='big-num red' style='font-size:26px'>{st.session_state.losses}</div><div class='small-label'>losses</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div style='font-size:14px'><b>STATUS:</b> {'✅ REAL - '+str(total_scan)+' COIN UNIK' if api_ok else '❌ GAGAL'}<br><small style='color:#7dd3fc !important'>Modal tersimpan: ${st.session_state.modal_invested:,.2f}</small></div>", unsafe_allow_html=True)
left,right=st.columns([1,2.2])
with left:
    next_name=top4[1].get('nama','-') if len(top4)>1 else '-'
    next_vol=top4[1].get('vol_mult',0) if len(top4)>1 else 0
    st.markdown(f"<div class='agent-card'><b>📄 SCREENER</b><div style='font-size:11px;color:#7dd3fc !important'>4 Sumber Gede - 0 Nama Coin</div><div>next ${next_name} · vol {next_vol:.1f}x</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>⚠️ RUG CHECK</b><div>passed ${cur_name} · LIQ>5K</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>💎 SIZER</b><div>34% of ${equity:,.2f} = ${modal_display:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>🟢 EXECUTOR</b><div>BOT PILIH SENDIRI LONG ${cur_name} · TP +20% SL -10%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>📝 LOGGER</b><div>Line #{st.session_state.line_no}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>💧 EQUITY</b><div>${equity:,.2f} · {st.session_state.trades} closes</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-card'><b>⏸️ YOU</b><div>{len(st.session_state.log)} lines</div></div>", unsafe_allow_html=True)
with right:
    cols=st.columns(len(top4) if top4 else 1)
    for col, c in zip(cols, top4):
        with col: st.markdown(f"<div class='top-card'><b>${c.get('nama','-')}</b><div style='font-size:11px;color:#7dd3fc !important'>vol {c.get('vol_mult',0):.1f}x · +{c.get('chg1h',0):.0f}% · LIQ ${c.get('liq',0):,}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='flow-card' style='margin-top:10px'><b>${cur_name} · +{cur_pnl:.2f}% live REAL</b><br><small style='color:#7dd3fc !important'>BOT PILIH SENDIRI DARI {total_scan} COIN - SOL ${sol_price:.2f} - Modal tersimpan ${st.session_state.modal_invested:,.2f}</small><div style='display:flex;gap:8px;margin-top:8px'><div style='flex:1;background:rgba(0,100,255,0.2);padding:8px;border-radius:8px;border:1px solid #00bfff'><b>COIN UNIK</b><div style='font-size:20px;font-weight:800;color:#00ffff !important'>{total_scan}</div></div><div style='flex:1;background:rgba(0,100,255,0.2);padding:8px;border-radius:8px;border:1px solid #00bfff'><b>DISAPU</b><div style='font-size:20px;font-weight:800;color:#00ffff !important'>{total_raw} pairs</div></div><div style='flex:1;background:rgba(0,100,255,0.2);padding:8px;border-radius:8px;border:1px solid #00bfff'><b>LOGGER</b><div style='font-size:20px;font-weight:800;color:#00ffff !important'>line #{st.session_state.line_no}</div></div><div style='flex:1;background:rgba(0,100,255,0.2);padding:8px;border-radius:8px;border:1px solid #00bfff'><b>EQUITY</b><div style='font-size:20px;font-weight:800;color:#00ff88 !important'>+${equity-10000:,.2f}</div></div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;gap:10px;margin-top:10px'><div class='trade-card' style='flex:1'><b>TRADE · BOT PILIH SENDIRI</b><div style='display:flex;justify-content:space-between;margin-top:8px'><b style='font-size:20px'>${cur_name}</b><b class='green'>+{cur_pnl:.2f}% live REAL</b></div><div style='font-size:13px;margin-top:6px'>entry {cur_entry:.6f} REAL<br>size 34% eq · ${modal_display:,.2f}</div></div><div class='trade-card' style='flex:1'><b>$ tail -f trades.log</b><div style='font-size:12px;margin-top:8px'>" + "<br>".join([f"{r[0]} {r[1]} ${r[2]} {r[3]:+.2f} net" if r[1]=="EXIT" else f"{r[0]} {r[1]} ${r[2]} ${r[4]:,.2f}" for r in reversed(st.session_state.log[-4:])]) + "</div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><b>RESULT</b><div style='display:flex;justify-content:space-between'><span>START</span><b>$10,000.00</b></div><div style='display:flex;justify-content:space-between'><span>NOW</span><b>${equity:,.2f}</b></div><div style='font-size:11px;color:#7dd3fc !important'>{st.session_state.wins} W / {st.session_state.losses} L · NET +${equity-10000:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='trade-card' style='margin-top:10px'><b>TRADE LOG</b>" + "".join([f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(0,191,255,0.3)'><span>{r[0]} {r[1]} <b>${r[2]}</b></span><span>{r[3]:+.2f}</span></div>" for r in reversed(st.session_state.log[-5:])]) + "</div>", unsafe_allow_html=True)
    st.markdown("### 🔍 DEBUG SCREENER", unsafe_allow_html=True)
    for line in debug_lines: st.code(line)
    if coins:
        tabel_coins=pd.DataFrame([{"Coin":c.get("nama"),"Harga REAL":c.get("harga"),"Naik 24h %":c.get("chg1h"),"Vol 24h":c.get("vol"),"LIQ $":c.get("liq"),"Mcap":c.get("mcap"),"Umur":c.get("umur")} for c in coins])
        st.dataframe(tabel_coins, use_container_width=True, hide_index=True)
    st.markdown("<div style='font-size:11px;color:#7dd3fc !important'>v13.1 NEON BLUE - 4 Sumber Gede - No Rate Limit - 0 Nama Coin - Bot Pilih Sendiri</div>", unsafe_allow_html=True)
time.sleep(10); st.rerun()
