"""
Configuration for paper trading simulation.
Adjust these values to test different risk and filter criteria.
"""

# ---------- CAPITAL & RISK ----------
STARTING_EQUITY = 1000.0
RISK_PER_TRADE = 0.01          # 1% máximo do equity por trade
MAX_PORTFOLIO_HEAT = 0.04      # risco total aberto ≤ 4%
KILL_SWITCH_DD = 0.10          # stop se equity cair 10% do início
ASSUMED_STOP_DISTANCE = 0.25   # 25% stop típico em alts voláteis

# ---------- SIMULATION ----------
MAX_TRADES = 100
SLIPPAGE_PCT = 0.08            # 8% slippage realista em baixa liquidez

# ---------- HARD FILTERS ----------
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
