import streamlit as st
import urllib.request, json, time
import pandas as pd
st.set_page_config(page_title="MEME NAGA BIRU - GMGN", page_icon="🐉", layout="wide")
st.title("🐉 MEME NAGA BIRU - GMGN + DEX + PUMP")
st.caption("GMGN Smart Money | DexScreener | Pump.fun | AUTO FOMO NON-STOP")
if "cash" not in st.session_state:
    st.session_state.cash=1000.0;st.session_state.wins=0;st.session_state.losses=0
    st.session_state.punya=None;st.session_state.beli=0;st.session_state.jumlah=0
    st.session_state.equity_hist=[1000.0];st.session_state.log=[];st.session_state.running=True
    st.session_state.scan_count=0;st.session_state.peak=0;st.session_state.sumber="-"
def get_json(url):
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://gmgn.ai/"})
        with urllib.request.urlopen(req, timeout=8) as r: return json.loads(r.read().decode())
    except: return None
@st.cache_data(ttl=8)
def scan_all():
    coins=[]
    for url in ["https://gmgn.ai/definition/api/v1/token/trending/sol?limit=20&orderby=volume&direction=desc"]:
        d=get_json(url)
        if d:
            data=d.get("data",d) if isinstance(d,dict) else d
            if isinstance(data,list):
                for t in data[:20]:
                    try:
                        harga=float(t.get("price",t.get("priceUsd",0)) or 0)
                        if harga<=0: continue
                        chg=float(t.get("priceChange1h",0) or 0); vol=float(t.get("volume1h",t.get("volume",0)) or 0)
                        coins.append({"nama":t.get("symbol","?"),"harga":harga,"chg5m":float(t.get("priceChange5m",0) or 0),"chg1h":chg,"vol1h":vol,"liq":float(t.get("liquidity",0) or 0),"mcap":float(t.get("marketCap",0) or 0),"fomo":chg*2+(vol/10000),"sumber":"GMGN"})
                    except: continue
    for q in ["pump","SOL","BONK"]:
        data=get_json(f"https://api.dexscreener.com/latest/dex/search/?q={q}")
        if data:
            for p in data.get("pairs",[])[:15]:
                try:
                    if p.get("chainId")!="solana": continue
                    vol=float(p.get("volume",{}).get("h1",0) or 0); liq=float(p.get("liquidity",{}).get("usd",0) or 0)
                    if vol<5000 or liq<5000: continue
                    harga=float(p.get("priceUsd",0) or 0)
                    if harga<=0: continue
                    chg1h=float(p.get("priceChange",{}).get("h1",0) or 0); chg5m=float(p.get("priceChange",{}).get("m5",0) or 0)
                    coins.append({"nama":p.get("baseToken",{}).get("symbol","?"),"harga":harga,"chg5m":chg5m,"chg1h":chg1h,"vol1h":vol,"liq":liq,"mcap":float(p.get("fdv",0) or 0),"fomo":chg5m*2+chg1h+(vol/10000),"sumber":"DEX/PUMP"})
                except: continue
    unik={}
    for c in coins:
        if c["nama"] not in unik or c["fomo"]>unik[c["nama"]]["fomo"]: unik[c["nama"]]=c
    hasil=sorted(unik.values(), key=lambda x: x["fomo"], reverse=True)[:10]
    if not hasil: hasil=[{"nama":"BONK","harga":0.00002,"chg5m":2.1,"chg1h":5.2,"vol1h":50000,"liq":100000,"mcap":1000000,"fomo":10,"sumber":"FALLBACK"}]
    return hasil
coins=scan_all(); st.session_state.scan_count+=1
harga_pegang=None
if st.session_state.punya:
    for c in coins:
        if c["nama"]==st.session_state.punya: harga_pegang=c["harga"]; break
status="💤 PAUSE"; aksi=""
if st.session_state.running:
    status=f"🤖 GMGN AUTO JALAN - Scan ke-{st.session_state.scan_count}"
    top=coins[0] if coins else None
    if not st.session_state.punya and top and top["fomo"]>5 and top["chg5m"]>0.5 and st.session_state.cash>=50:
        st.session_state.cash-=50; st.session_state.punya=top["nama"]; st.session_state.beli=top["harga"]; st.session_state.jumlah=50/top["harga"]; st.session_state.peak=top["harga"]; st.session_state.sumber=top.get("sumber","-")
        st.session_state.log.append(f"🟢 BUY [{top.get('sumber','-')}] {top['nama']} $50 @ ${top['harga']:.6f} | FOMO {top['fomo']:.1f} | 5m {top['chg5m']:.1f}% | Vol ${top['vol1h']:,.0f}")
        harga_pegang=top["harga"]; aksi=f"BARU BELI {top['nama']} dari {top.get('sumber','-')}"
    elif st.session_state.punya and harga_pegang:
        pp=(harga_pegang-st.session_state.beli)/st.session_state.beli*100
        if harga_pegang>st.session_state.peak: st.session_state.peak=harga_pegang
        turun=(harga_pegang-st.session_state.peak)/st.session_state.peak*100 if st.session_state.peak>0 else 0
        alasan=""
        if pp>=3.0: alasan=f"TP +{pp:.1f}%"
        elif pp<=-2.0: alasan=f"SL {pp:.1f}%"
        elif pp>1.0 and turun<=-1.5: alasan=f"TRAILING {pp:.1f}%"
        if alasan:
            hasil=st.session_state.jumlah*harga_pegang; profit=hasil-50; st.session_state.cash+=hasil
            if profit>0: st.session_state.wins+=1
            else: st.session_state.losses+=1
            st.session_state.log.append(f"🔴 SELL {st.session_state.punya} {alasan} Profit ${profit:.2f}")
            st.session_state.punya=None; st.session_state.jumlah=0; st.session_state.peak=0; aksi=f"BARU JUAL - {alasan}"
nilai=st.session_state.jumlah*harga_pegang if (st.session_state.punya and harga_pegang) else 0
equity=st.session_state.cash+nilai; cuan=equity-1000.0
st.session_state.equity_hist.append(equity)
if len(st.session_state.equity_hist)>60: st.session_state.equity_hist=st.session_state.equity_hist[-60:]
st.info(status)
if aksi: st.success(f"⚡ {aksi}")
c1,c2,c3,c4=st.columns(4)
c1.metric("MODAL","$1000"); c2.metric("CUAN",f"${cuan:,.2f}"); c3.metric("EQUITY",f"${equity:,.2f}"); c4.metric("MENANG / KALAH",f"{st.session_state.wins} / {st.session_state.losses}")
st.metric("CASH",f"${st.session_state.cash:,.2f} | Sumber: {st.session_state.sumber}")
s1,s2=st.columns(2)
if s1.button("▶️ START AUTO GMGN",use_container_width=True,type="primary"): st.session_state.running=True; st.rerun()
if s2.button("⏸️ PAUSE",use_container_width=True): st.session_state.running=False; st.rerun()
if st.button("🔄 RESET BOT"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()
is_up=equity>=1000; warna="#00FF88" if is_up else "#FF3355"
st.subheader("📊 Grafik Equity"); st.markdown(f"<h3 style='color:{warna}'>{'▲ NAIK' if is_up else '▼ TURUN'} - ${equity:,.2f}</h3>",unsafe_allow_html=True)
st.line_chart(pd.DataFrame({"Equity":st.session_state.equity_hist}),color=warna)
if st.session_state.punya and harga_pegang:
    pp=(harga_pegang-st.session_state.beli)/st.session_state.beli*100
    st.info(f"📌 PEGANG: {st.session_state.punya} | Beli ${st.session_state.beli:.6f} -> Skrg ${harga_pegang:.6f} | Profit {pp:.2f}%")
else: st.write("💤 Belum pegang - Bot lagi scan GMGN...")
st.divider(); st.subheader("🔥 TOP 10 GMGN / DEX / PUMP TRENDING")
for i,c in enumerate(coins):
    e="🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
    st.write(f"{e} **{c['nama']}** [{c.get('sumber','-')}] | ${c['harga']:.6f} | 5m {c['chg5m']:.1f}% | 1j {c['chg1h']:.1f}% | Vol ${c['vol1h']:,.0f} | FOMO {c['fomo']:.1f}")
st.divider(); st.subheader("📜 Log Auto Bot")
for h in reversed(st.session_state.log[-15:]): st.write(h)
st.divider(); st.subheader("🏦 Deposit & Withdraw")
d1,d2=st.columns(2)
with d1:
    dep=st.number_input("Deposit ($)",min_value=10.0,value=100.0,step=10.0,key="dep")
    if st.button("➕ Deposit",use_container_width=True): st.session_state.cash+=dep; st.session_state.log.append(f"DEPOSIT +${dep:.2f}"); st.rerun()
with d2:
    wd=st.number_input("Withdraw ($)",min_value=10.0,value=100.0,step=10.0,key="wd")
    if st.button("➖ Withdraw",use_container_width=True):
        if wd<=st.session_state.cash: st.session_state.cash-=wd; st.session_state.log.append(f"WITHDRAW -${wd:.2f}"); st.rerun()
if st.session_state.running: time.sleep(10); st.rerun()
