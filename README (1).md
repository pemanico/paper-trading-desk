# Paper Trading Desk - Professional Risk Simulation

Skeleton for paper trading simulation of Solana-style altcoins using professional risk management criteria.

## Structure
- `config.py` — All simulation parameters (risk, filters, slippage)
- `skeleton_paper.py` — Core simulation
- `app.py` — Streamlit visualizer
- `requirements.txt` — Dependencies

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run simulation
```bash
python skeleton_paper.py
```

## Run visualizer
```bash
streamlit run app.py
```

The app has a **Run new simulation** button at the top.
If the button does not appear, pull the latest code and restart Streamlit.

## Notes
- High rejection rates are expected with strict professional filters.
- Expectancy is typically negative or near zero in high-friction low-liquidity markets.
- This is for learning the process, not for live trading.
