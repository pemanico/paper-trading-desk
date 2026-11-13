#!/usr/bin/env python3
"""
Esqueleto - Critério de analistas sérios
Paper trading simulation.
Hard filters + proper risk-based sizing + additional professional parameters
+ slippage + logging + expectancy.

O que analistas sérios fazem de verdade:
- Risco por trade ≤ 1% do capital, calculado a partir da distância ao stop.
- Portfolio heat limitado.
- Filtros de qualidade de dados (volume/mcap, funding extremos, idade).
- Não se focam em memecoins frescas sem estrutura.
Este script simula isso de forma brutalmente realista para o universo de alts de baixa liquidez.

Run: python skeleton_paper.py
"""

import csv
import random
from datetime import datetime
from dataclasses import dataclass, asdict

# ---------- CONFIG ----------
STARTING_EQUITY = 1000.0
RISK_PER_TRADE = 0.01          # 1% máximo do equity por trade
MAX_PORTFOLIO_HEAT = 0.04      # risco total aberto ≤ 4%
MAX_TRADES = 100
SLIPPAGE_PCT = 0.08
KILL_SWITCH_DD = 0.10
ASSUMED_STOP_DISTANCE = 0.25   # 25% stop típico em alts voláteis (simulado)

# Hard filters
MIN_LIQUIDITY_USD = 20000
MAX_TOP10_PCT = 22.0
MAX_DEV_HOLD_PCT = 4.0
MIN_LP_LOCKED_PCT = 95.0
MIN_AGE_HOURS = 2.0
MIN_VOLUME_TO_MCAP = 0.02      # 2%
MAX_VOLUME_TO_MCAP = 0.40      # acima disto é suspeito de wash
MAX_ABS_FUNDING = 0.0008       # ~0.08% ; extremos rejeitam

REQUIRE_MINT_REVOKED = True
REQUIRE_FREEZE_REVOKED = True

# ---------- DATA ----------
@dataclass
class Candidate:
    symbol: str
    liquidity_usd: float
    top10_pct: float
    dev_hold_pct: float
    lp_locked_pct: float
    mint_revoked: bool
    freeze_revoked: bool
    age_hours: float
    volume_24h: float
    mcap: float
    funding_rate: float          # simulado; 0 se não tiver perp
    has_perp: bool
    is_rugged: bool = False

    @property
    def vol_to_mcap(self) -> float:
        return self.volume_24h / max(self.mcap, 1)

@dataclass
class TradeLog:
    timestamp: str
    symbol: str
    decision: str
    reason: str
    size_usd: float
    risk_usd: float
    entry_price_sim: float
    exit_price_sim: float
    pnl_usd: float
    equity_after: float
    slippage_applied: float
    vol_to_mcap: float
    funding: float

# ---------- GENERATOR ----------
def generate_candidate(i: int) -> Candidate:
    liq = random.choice([5000, 12000, 25000, 40000, 80000, 150000, 300000])
    mcap = liq * random.uniform(3, 40)
    vol = mcap * random.uniform(0.005, 0.8)
    has_perp = random.random() < 0.25  # poucos têm
    funding = random.gauss(0.0001, 0.0004) if has_perp else 0.0
    return Candidate(
        symbol=f"MEME{i:03d}",
        liquidity_usd=liq,
        top10_pct=random.uniform(6, 50),
        dev_hold_pct=random.uniform(0, 10),
        lp_locked_pct=random.choice([0, 50, 80, 95, 99, 100]),
        mint_revoked=random.choices([True, False], weights=[0.8, 0.2])[0],
        freeze_revoked=random.choices([True, False], weights=[0.88, 0.12])[0],
        age_hours=random.uniform(0.3, 48),
        volume_24h=vol,
        mcap=mcap,
        funding_rate=funding,
        has_perp=has_perp,
        is_rugged=random.random() < 0.07
    )

# ---------- FILTER ----------
def check_filters(c: Candidate) -> tuple[bool, str]:
    if c.is_rugged:
        return False, "already rugged"
    if REQUIRE_MINT_REVOKED and not c.mint_revoked:
        return False, "mint authority active"
    if REQUIRE_FREEZE_REVOKED and not c.freeze_revoked:
        return False, "freeze authority active"
    if c.liquidity_usd < MIN_LIQUIDITY_USD:
        return False, f"liq ${c.liquidity_usd:.0f} too low"
    if c.top10_pct > MAX_TOP10_PCT:
        return False, f"top10 {c.top10_pct:.1f}%"
    if c.dev_hold_pct > MAX_DEV_HOLD_PCT:
        return False, f"dev {c.dev_hold_pct:.1f}%"
    if c.lp_locked_pct < MIN_LP_LOCKED_PCT:
        return False, f"LP locked {c.lp_locked_pct:.0f}%"
    if c.age_hours < MIN_AGE_HOURS:
        return False, f"age {c.age_hours:.1f}h too young"
    vtm = c.vol_to_mcap
    if vtm < MIN_VOLUME_TO_MCAP or vtm > MAX_VOLUME_TO_MCAP:
        return False, f"vol/mcap {vtm:.2%} out of range"
    if c.has_perp and abs(c.funding_rate) > MAX_ABS_FUNDING:
        return False, f"funding extreme {c.funding_rate:.5f}"
    return True, "passed professional filters"

# ---------- OUTCOME ----------
def simulate_outcome() -> tuple[float, float]:
    roll = random.random()
    if roll < 0.60:
        return random.uniform(-0.45, -0.18), SLIPPAGE_PCT
    elif roll < 0.85:
        return random.uniform(0.08, 0.35), SLIPPAGE_PCT
    else:
        return random.uniform(0.4, 1.8), SLIPPAGE_PCT * 0.6

# ---------- MAIN ----------
def run_simulation():
    equity = STARTING_EQUITY
    logs = []
    entered = 0
    rejected = 0
    peak = equity
    open_risk = 0.0  # simplified; we close immediately in this sim

    print(f"Starting equity: ${equity:.2f}")
    print(f"Risk per trade: {RISK_PER_TRADE*100:.1f}% | Assumed stop: {ASSUMED_STOP_DISTANCE*100:.0f}%\n")

    for i in range(1, MAX_TRADES + 1):
        if equity <= STARTING_EQUITY * (1 - KILL_SWITCH_DD):
            print(f"KILL SWITCH at candidate {i}")
            break

        c = generate_candidate(i)
        passed, reason = check_filters(c)

        size_usd = 0.0
        risk_usd = 0.0
        pnl_usd = 0.0
        entry_sim = 1.0
        exit_sim = 1.0
        slip = 0.0
        decision = "REJECT"

        if passed:
            # Professional sizing: risk_usd / stop_distance
            risk_usd = equity * RISK_PER_TRADE
            if open_risk + risk_usd > equity * MAX_PORTFOLIO_HEAT:
                decision = "REJECT"
                reason = "portfolio heat limit"
            else:
                decision = "ENTER"
                entered += 1
                size_usd = risk_usd / ASSUMED_STOP_DISTANCE
                mult, slip = simulate_outcome()
                effective_mult = mult * (1 - slip)
                pnl_usd = size_usd * effective_mult
                equity += pnl_usd
                entry_sim = 1.0
                exit_sim = 1.0 * (1 + effective_mult)
                # open_risk would be managed in real system; here we "close" immediately
        else:
            rejected += 1

        peak = max(peak, equity)

        log = TradeLog(
            timestamp=datetime.utcnow().isoformat(timespec="seconds"),
            symbol=c.symbol,
            decision=decision,
            reason=reason,
            size_usd=round(size_usd, 2),
            risk_usd=round(risk_usd, 2),
            entry_price_sim=round(entry_sim, 4),
            exit_price_sim=round(exit_sim, 4),
            pnl_usd=round(pnl_usd, 2),
            equity_after=round(equity, 2),
            slippage_applied=round(slip, 3),
            vol_to_mcap=round(c.vol_to_mcap, 4),
            funding=round(c.funding_rate, 6)
        )
        logs.append(log)

        if i % 25 == 0 or (passed and entered <= 5):
            print(f"{decision:6} {c.symbol} | {reason[:42]:42} | eq ${equity:.0f}")

    # Summary
    wins = sum(1 for l in logs if l.decision == "ENTER" and l.pnl_usd > 0)
    losses = sum(1 for l in logs if l.decision == "ENTER" and l.pnl_usd <= 0)
    total_entered = entered
    win_rate = (wins / total_entered * 100) if total_entered else 0
    total_pnl = equity - STARTING_EQUITY
    avg_r = total_pnl / max(total_entered, 1)

    print("\n" + "="*60)
    print("SUMMARY (critério de analistas sérios)")
    print("="*60)
    print(f"Candidates : {len(logs)}")
    print(f"Rejected   : {rejected} ({rejected/len(logs)*100:.1f}%)")
    print(f"Entered    : {entered}")
    print(f"Wins/Losses: {wins}/{losses}  |  Win rate: {win_rate:.1f}%")
    print(f"Start equity : ${STARTING_EQUITY:.2f}")
    print(f"Final equity : ${equity:.2f}")
    print(f"Total PnL    : ${total_pnl:.2f}")
    print(f"Expectancy / trade : ${avg_r:.2f}")
    print(f"Max DD approx : {(peak - min((l.equity_after for l in logs), default=equity))/peak*100:.1f}%")

    with open("paper_log.csv", "w", newline="") as f:
        if logs:
            w = csv.DictWriter(f, fieldnames=asdict(logs[0]).keys())
            w.writeheader()
            for log in logs:
                w.writerow(asdict(log))
    print("\nLog: paper_log.csv")
    print("Isto é o que o processo de analistas sérios produz em mercados de alta fricção:")
    print("muitos rejects, sizing baseado em risco real, expectancy que raramente é positiva.")

if __name__ == "__main__":
    random.seed(42)
    run_simulation()
