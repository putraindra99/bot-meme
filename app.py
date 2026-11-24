#!/usr/bin/env python3
"""
PAPERBOT - bot paper trading meme coin Solana (TIDAK memakai uang asli).
Alur: SCAN -> SHIELD -> SCORE -> FIRE (virtual) -> HARVEST (trailing/tier) -> LOG

Jalankan:
  python paperbot.py --mock            # data simulasi (tes offline)
  python paperbot.py                   # data live: DexScreener + RugCheck + Jupiter
Tanpa dependensi (stdlib saja). Tidak ada private key, tidak ada transaksi on-chain.
"""
import argparse, json, math, random, time, urllib.request, urllib.parse
from dataclasses import dataclass, field

SOL = "So11111111111111111111111111111111111111112"


@dataclass
class Cfg:
    start_balance: float = 1000.0
    size_pct: float = 0.05        # 5% saldo per posisi
    max_positions: int = 5
    max_slip: float = 0.015       # tolak fill jika slippage > 1.5%
    fee: float = 0.003            # 0.3% per sisi (fee + priority, perkiraan)
    min_liq: float = 25_000
    min_age_min: int = 10
    score_min: float = 0.60
    hard_stop: float = -0.20      # cut loss -20%
    trail: float = 0.15           # trailing 15% dari puncak
    tiers: tuple = ((0.30, 1 / 3), (0.60, 1 / 3))  # (profit, porsi dijual)
    max_hold_min: int = 240
    log_file: str = "night.log.jsonl"


# ---------------------------------------------------------------- sumber data
def http(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "paperbot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class LiveSource:
    seen = set()

    def candidates(self):
        out = []
        try:
            prof = http("https://api.dexscreener.com/token-profiles/latest/v1")
            mints = [p["tokenAddress"] for p in prof if p.get("chainId") == "solana"]
            mints = [m for m in mints if m not in self.seen][:30]
            if not mints:
                return out
            data = http("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(mints))
            best = {}
            for p in data.get("pairs") or []:
                if p.get("chainId") != "solana":
                    continue
                m = p["baseToken"]["address"]
                if m not in best or (p.get("liquidity") or {}).get("usd", 0) > (best[m].get("liquidity") or {}).get("usd", 0):
                    best[m] = p
            for m, p in best.items():
                self.seen.add(m)
                tx = (p.get("txns") or {}).get("h1", {})
                out.append(dict(
                    mint=m, symbol=p["baseToken"]["symbol"], price=float(p.get("priceUsd") or 0),
                    liq=(p.get("liquidity") or {}).get("usd", 0),
                    vol_h1=(p.get("volume") or {}).get("h1", 0),
                    chg_m5=(p.get("priceChange") or {}).get("m5", 0) or 0,
                    chg_h1=(p.get("priceChange") or {}).get("h1", 0) or 0,
                    buys=tx.get("buys", 0), sells=tx.get("sells", 0),
                    age_min=(time.time() * 1000 - (p.get("pairCreatedAt") or 0)) / 60000))
        except Exception as e:
            print("scan error:", e)
        return out

    def price(self, mint):
        try:
            d = http("https://api.dexscreener.com/latest/dex/tokens/" + mint)
            ps = [p for p in d.get("pairs") or [] if p.get("chainId") == "solana"]
            ps.sort(key=lambda p: (p.get("liquidity") or {}).get("usd", 0), reverse=True)
            return float(ps[0]["priceUsd"])
        except Exception:
            return None

    def shield(self, c):
        # 1) RugCheck: blokir jika ada risiko level "danger" (fail-closed)
        try:
            r = http(f"https://api.rugcheck.xyz/v1/tokens/{c['mint']}/report/summary")
            bad = [x["name"] for x in r.get("risks", []) if x.get("level") == "danger"]
            if bad:
                return False, "rugcheck: " + ", ".join(bad[:2])
        except Exception as e:
            return False, f"rugcheck gagal ({e.__class__.__name__})"
        # 2) Honeypot sim: beli 0.1 SOL lalu jual balik lewat quote Jupiter
        try:
            q = "https://lite-api.jup.ag/swap/v1/quote?inputMint=%s&outputMint=%s&amount=%d&slippageBps=300"
            buy = http(q % (SOL, c["mint"], 100_000_000))
            sell = http(q % (c["mint"], SOL, int(buy["outAmount"])))
            loss = 1 - int(sell["outAmount"]) / 100_000_000
            if loss > 0.25:
                return False, f"round-trip rugi {loss:.0%} (pajak/honeypot)"
        except Exception:
            return False, "honeypot: rute jual tidak ada"
        return True, "ok"


class MockSource:
    """Data acak untuk tes offline. Sebagian token sengaja 'rug'."""
    def __init__(self, seed=7):
        random.seed(seed)
        self.t = {}
        self.n = 0

    def candidates(self):
        out = []
        if random.random() < 0.35:
            self.n += 1
            m = f"MOCK{self.n}"
            drift = random.gauss(0.0005, 0.004)
            rug = random.random() < 0.18
            honey = random.random() < 0.07
            self.t[m] = dict(p=random.uniform(1e-5, 1e-3), drift=drift, rug=rug,
                             rug_at=random.randint(5, 40), age=0, honey=honey, shield_sees=random.random() < 0.7)
            good = drift > 0
            out.append(dict(mint=m, symbol=f"$M{self.n}", price=self.t[m]["p"],
                            liq=random.uniform(15e3, 200e3), vol_h1=random.uniform(5e3, 250e3),
                            chg_m5=random.gauss(6 if good else 1, 4), chg_h1=random.gauss(40 if good else 8, 25),
                            buys=random.randint(80, 400), sells=random.randint(40, 300), age_min=random.randint(5, 90)))
        return out

    def price(self, mint):
        s = self.t[mint]
        s["age"] += 1
        s["p"] *= math.exp(random.gauss(s["drift"], 0.03))
        if s["rug"] and s["age"] == s["rug_at"]:
            s["p"] *= 0.05
        return s["p"]

    def shield(self, c):
        s = self.t[c["mint"]]
        if s["honey"]:
            return False, "honeypot: sell sim failed"
        if s["rug"] and s["shield_sees"]:
            return False, "LP unlocked / top10 holders tinggi"
        return True, "ok"


# ---------------------------------------------------------------- broker paper
@dataclass
class Pos:
    mint: str; symbol: str; entry: float; qty: float; cost: float
    peak: float; opened: float; tier: int = 0; realized: float = 0.0


class Paper:
    def __init__(self, cfg):
        self.cfg, self.cash, self.pos = cfg, cfg.start_balance, {}
        self.wins = self.losses = self.rugs = self.fired = 0
        self.f = open(cfg.log_file, "a")

    def log(self, **kw):
        kw["t"] = time.strftime("%H:%M:%S")
        print(" ".join(f"{k}={v}" for k, v in kw.items()))
        self.f.write(json.dumps(kw) + "\n"); self.f.flush()

    def slip(self, size, liq):
        # slippage simulasi: dasar 0.3% + dampak ukuran vs likuiditas + noise
        return 0.003 + (size / max(liq, 1)) * 2 + random.uniform(0, 0.006)

    def equity(self, prices):
        return self.cash + sum(p.qty * prices.get(m, p.entry) for m, p in self.pos.items())

    def buy(self, c):
        size = self.cash * self.cfg.size_pct
        s = self.slip(size, c["liq"])
        if s > self.cfg.max_slip:
            self.log(ev="SKIP", sym=c["symbol"], why=f"slip {s:.2%} > max"); return
        px = c["price"] * (1 + s)
        qty = size * (1 - self.cfg.fee) / px
        self.cash -= size
        self.pos[c["mint"]] = Pos(c["mint"], c["symbol"], px, qty, size, px, time.time())
        self.fired += 1
        self.log(ev="FIRE", sym=c["symbol"], size=round(size, 2), slip=f"{s:.2%}", score=c["score"])

    def sell(self, p, frac, price, why, liq=50_000):
        q = p.qty * frac if frac < 1 else p.qty
        s = self.slip(q * price, liq)
        proceeds = q * price * (1 - s) * (1 - self.cfg.fee)
        self.cash += proceeds
        p.realized += proceeds
        p.qty -= q
        return proceeds, why

    def manage(self, source):
        prices = {}
        for m, p in list(self.pos.items()):
            px = source.price(m)
            if px is None:
                continue
            prices[m] = px
            p.peak = max(p.peak, px)
            gain = px / p.entry - 1
            age = (time.time() - p.opened) / 60
            # tier take-profit
            if p.tier < len(self.cfg.tiers) and gain >= self.cfg.tiers[p.tier][0]:
                self.sell(p, self.cfg.tiers[p.tier][1] * p.cost / p.cost, px, "tier")
                self.log(ev="SCALE", sym=p.symbol, tier=p.tier + 1, gain=f"{gain:.0%}")
                p.tier += 1
                continue
            reason = None
            if gain <= self.cfg.hard_stop:
                reason = "hard stop"
            elif px <= p.peak * (1 - self.cfg.trail) and p.tier > 0:
                reason = "trail hit"
            elif age >= self.cfg.max_hold_min:
                reason = "time exit"
            if reason:
                if gain < -0.6:
                    self.rugs += 1
                self.sell(p, 1.0, px, reason)
                pnl = p.realized - p.cost
                self.wins += pnl > 0
                self.losses += pnl <= 0
                self.log(ev="EXIT", sym=p.symbol, pnl=round(pnl, 2), why=reason)
                del self.pos[m]
        return prices


# ---------------------------------------------------------------- strategi
def score(c):
    vr = min(c["vol_h1"] / max(c["liq"], 1) / 1.5, 1)
    mom = 0.5 * min(max(c["chg_m5"] / 10, 0), 1) + 0.5 * min(max(c["chg_h1"] / 50, 0), 1)
    tot = c["buys"] + c["sells"]
    flow = c["buys"] / tot if tot else 0
    return round(0.35 * vr + 0.35 * mom + 0.30 * flow, 2)


def run(a):
    cfg = Cfg()
    src = MockSource() if a.mock else LiveSource()
    br = Paper(cfg)
    blocked = checked = 0
    for tick in range(a.ticks):
        for c in src.candidates():                       # SCAN
            checked += 1
            if len(br.pos) >= cfg.max_positions or c["liq"] < cfg.min_liq or c["age_min"] < cfg.min_age_min:
                continue
            ok, why = src.shield(c)                      # SHIELD
            if not ok:
                blocked += 1
                br.log(ev="FILTERED", sym=c["symbol"], why=why); continue
            c["score"] = score(c)                        # SCORE
            if c["score"] >= cfg.score_min:
                br.buy(c)                                # FIRE (virtual)
        prices = br.manage(src)                          # HARVEST
        if tick % 20 == 0:
            br.log(ev="STATUS", equity=round(br.equity(prices), 2), open=len(br.pos),
                   W=br.wins, L=br.losses, blocked=blocked, checked=checked)
        time.sleep(0 if a.mock else a.interval)
    eq = br.equity({m: src.price(m) or p.entry for m, p in br.pos.items()})
    n = br.wins + br.losses
    print(f"\n=== RINGKASAN (PAPER) ===\nEquity: ${eq:,.2f} (mulai ${cfg.start_balance:,.0f}) "
          f"| Trade: {n} | Win: {br.wins} ({br.wins / n:.0%} win rate)" if n else "\nBelum ada trade selesai.")
    print(f"Rug diblok: {blocked} | Rug kena: {br.rugs}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--interval", type=int, default=30, help="detik antar siklus (live)")
    run(ap.parse_args())
